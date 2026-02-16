"""
Database utilities for storing agent debates, positions, and market snapshots.
Enables historical tracking, outcome validation, and learning over time.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd


class DebateDatabase:
    def __init__(self, db_path: str = "agent_debates.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Debates table: stores each complete debate session
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                final_recommendation TEXT,
                consensus_score REAL,
                session_cost REAL,
                debate_rounds INTEGER DEFAULT 3,
                validation_status TEXT,
                validation_date DATETIME,
                validation_accuracy REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Agent positions: stores each agent's stance in each round
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debate_id INTEGER NOT NULL,
                agent_role TEXT NOT NULL,
                round_number INTEGER NOT NULL,
                position TEXT NOT NULL,
                confidence REAL,
                reasoning TEXT,
                challenges TEXT,
                responses TEXT,
                FOREIGN KEY (debate_id) REFERENCES debates(id)
            )
        """)
        
        # Market snapshots: stores market data at time of debate
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debate_id INTEGER NOT NULL,
                mortgage_rate REAL,
                home_price_index REAL,
                rate_12mo_avg REAL,
                price_yoy_change REAL,
                snapshot_date DATETIME NOT NULL,
                FOREIGN KEY (debate_id) REFERENCES debates(id)
            )
        """)
        
        # Lessons learned: stores patterns extracted from validated outcomes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons_learned (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debate_id INTEGER NOT NULL,
                pattern_description TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                condition_description TEXT,
                accuracy_observed REAL,
                times_observed INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (debate_id) REFERENCES debates(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_debate(
        self, 
        final_recommendation: str,
        consensus_score: float,
        session_cost: float,
        agent_positions: List[Dict[str, Any]],
        market_snapshot: Dict[str, Any]
    ) -> int:
        """
        Save a complete debate session to the database.
        
        Returns:
            debate_id: The ID of the saved debate
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert debate record
        cursor.execute("""
            INSERT INTO debates (
                timestamp, final_recommendation, consensus_score, 
                session_cost, debate_rounds
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            final_recommendation,
            consensus_score,
            session_cost,
            3  # Fixed at 3 rounds for now
        ))
        
        debate_id = cursor.lastrowid
        
        # Insert agent positions
        for position in agent_positions:
            cursor.execute("""
                INSERT INTO agent_positions (
                    debate_id, agent_role, round_number, position,
                    confidence, reasoning, challenges, responses
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                debate_id,
                position.get('agent_role'),
                position.get('round_number'),
                position.get('position'),
                position.get('confidence'),
                position.get('reasoning'),
                position.get('challenges'),
                position.get('responses')
            ))
        
        # Insert market snapshot
        cursor.execute("""
            INSERT INTO market_snapshots (
                debate_id, mortgage_rate, home_price_index,
                rate_12mo_avg, price_yoy_change, snapshot_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            debate_id,
            market_snapshot.get('mortgage_rate'),
            market_snapshot.get('home_price_index'),
            market_snapshot.get('rate_12mo_avg'),
            market_snapshot.get('price_yoy_change'),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return int(debate_id) if debate_id else 0
    
    def get_recent_debates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent debates with basic info."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, timestamp, final_recommendation, consensus_score,
                session_cost, validation_status, validation_accuracy
            FROM debates
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_debate_details(self, debate_id: int) -> Optional[Dict[str, Any]]:
        """Get complete details of a specific debate including all rounds."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get debate info
        cursor.execute("""
            SELECT * FROM debates WHERE id = ?
        """, (debate_id,))
        
        debate_row = cursor.fetchone()
        if not debate_row:
            conn.close()
            return None
        
        debate_columns = [desc[0] for desc in cursor.description]
        debate = dict(zip(debate_columns, debate_row))
        
        # Get agent positions
        cursor.execute("""
            SELECT * FROM agent_positions 
            WHERE debate_id = ?
            ORDER BY round_number, agent_role
        """, (debate_id,))
        
        position_columns = [desc[0] for desc in cursor.description]
        positions = [dict(zip(position_columns, row)) for row in cursor.fetchall()]
        
        # Get market snapshot
        cursor.execute("""
            SELECT * FROM market_snapshots WHERE debate_id = ?
        """, (debate_id,))
        
        snapshot_row = cursor.fetchone()
        snapshot = None
        if snapshot_row:
            snapshot_columns = [desc[0] for desc in cursor.description]
            snapshot = dict(zip(snapshot_columns, snapshot_row))
        
        conn.close()
        
        return {
            'debate': debate,
            'positions': positions,
            'market_snapshot': snapshot
        }
    
    def validate_debate_outcome(
        self, 
        debate_id: int, 
        current_rate: float,
        validation_days: int = 30
    ) -> Dict[str, Any]:
        """
        Validate a past debate's recommendation against current market data.
        
        Returns:
            Dict with validation status and accuracy score
        """
        details = self.get_debate_details(debate_id)
        if not details or not details.get('market_snapshot'):
            return {'status': 'insufficient_data', 'accuracy': 0.0}
        
        original_rate = details['market_snapshot']['mortgage_rate']
        recommendation = details['debate']['final_recommendation']
        
        # Calculate rate change
        rate_change = current_rate - original_rate
        rate_change_pct = (rate_change / original_rate) * 100
        
        # Determine if prediction was correct
        accuracy = 0.0
        status = "incorrect"
        
        if recommendation and "bearish" in recommendation.lower():
            # Bearish = expected rates to rise or remain high
            if rate_change >= 0:
                status = "correct"
                accuracy = min(100.0, abs(rate_change_pct) * 20)  # Scale accuracy
        elif recommendation and "bullish" in recommendation.lower():
            # Bullish = expected rates to fall
            if rate_change < 0:
                status = "correct"
                accuracy = min(100.0, abs(rate_change_pct) * 20)
        else:
            # Neutral prediction
            if abs(rate_change_pct) < 5:  # Within 5% is neutral
                status = "correct"
                accuracy = 50.0
        
        # Update database with validation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE debates
            SET validation_status = ?,
                validation_date = ?,
                validation_accuracy = ?
            WHERE id = ?
        """, (status, datetime.now(), accuracy, debate_id))
        conn.commit()
        conn.close()
        
        # Extract pattern for future learning
        market_snapshot = details.get('market_snapshot', {})
        self.extract_pattern_from_validation(
            debate_id, status, accuracy, market_snapshot, recommendation
        )
        
        return {
            'status': status,
            'accuracy': accuracy,
            'rate_change': rate_change,
            'rate_change_pct': rate_change_pct
        }
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get overall statistics on validated debates."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_validated,
                AVG(validation_accuracy) as avg_accuracy,
                SUM(CASE WHEN validation_status = 'correct' THEN 1 ELSE 0 END) as correct_count
            FROM debates
            WHERE validation_status IS NOT NULL
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_validated': row[0],
                'avg_accuracy': round(row[1], 2) if row[1] else 0.0,
                'correct_count': row[2],
                'accuracy_rate': round((row[2] / row[0] * 100), 2) if row[0] > 0 else 0.0
            }
        
        return {'total_validated': 0, 'avg_accuracy': 0.0, 'correct_count': 0, 'accuracy_rate': 0.0}

    def get_accuracy_trend(self) -> List[Dict[str, Any]]:
        """Get prediction trend over time for all debates.
        
        Returns list of dicts with: debate_num, timestamp, accuracy, status, recommendation
        Shows all debates (validated and pending) for full prediction history.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                ROW_NUMBER() OVER (ORDER BY timestamp) as debate_num,
                timestamp,
                COALESCE(validation_accuracy, 50) as accuracy,
                COALESCE(validation_status, 'pending') as status,
                final_recommendation
            FROM debates
            ORDER BY timestamp ASC
        """)
        
        columns = ['debate_num', 'timestamp', 'accuracy', 'status', 'recommendation']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results    
    def extract_pattern_from_validation(
        self,
        debate_id: int,
        validation_status: str,
        accuracy: float,
        market_snapshot: Dict[str, Any],
        final_recommendation: str
    ) -> None:
        """Extract and store a learned pattern from a validation result."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine rate trend
        mortgage_rate = market_snapshot.get('mortgage_rate', 0)
        rate_12mo_avg = market_snapshot.get('rate_12mo_avg', mortgage_rate)
        rate_trend = "increasing" if mortgage_rate > rate_12mo_avg else "decreasing"
        
        # Determine prediction type
        prediction_type = "NEUTRAL"
        if final_recommendation:
            if "bullish" in final_recommendation.lower():
                prediction_type = "BULLISH"
            elif "bearish" in final_recommendation.lower():
                prediction_type = "BEARISH"
        
        # Create pattern description
        condition_desc = f"Market condition: rates {rate_trend}"
        pattern_desc = f"{prediction_type} prediction when {rate_trend}"
        
        # Check if similar pattern exists
        cursor.execute("""
            SELECT id, times_observed, accuracy_observed FROM lessons_learned
            WHERE prediction_type = ? AND condition_description = ?
            ORDER BY last_updated DESC LIMIT 1
        """, (prediction_type, condition_desc))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing pattern
            pattern_id, times_obs, avg_accuracy = existing
            new_times = times_obs + 1
            # Update average accuracy
            new_accuracy = (avg_accuracy * times_obs + accuracy) / new_times
            
            cursor.execute("""
                UPDATE lessons_learned
                SET times_observed = ?,
                    accuracy_observed = ?,
                    last_updated = ?
                WHERE id = ?
            """, (new_times, new_accuracy, datetime.now(), pattern_id))
        else:
            # Create new pattern
            cursor.execute("""
                INSERT INTO lessons_learned
                (debate_id, pattern_description, prediction_type, 
                 condition_description, accuracy_observed, times_observed)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (debate_id, pattern_desc, prediction_type, condition_desc, accuracy))
        
        conn.commit()
        conn.close()
    
    def get_learned_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top learned patterns by frequency and reliability."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                pattern_description,
                prediction_type,
                condition_description,
                accuracy_observed,
                times_observed
            FROM lessons_learned
            WHERE times_observed >= 2
            ORDER BY accuracy_observed DESC, times_observed DESC
            LIMIT ?
        """, (limit,))
        
        columns = ['pattern', 'prediction', 'condition', 'accuracy', 'frequency']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_patterns_summary_for_agents(self) -> str:
        """Generate a summary of learned patterns for agent context."""
        patterns = self.get_learned_patterns(limit=3)
        
        if not patterns:
            return ""
        
        summary = "\n### Historical Lessons Learned:\n"
        for i, p in enumerate(patterns, 1):
            summary += (
                f"{i}. {p['pattern']}\n"
                f"   - Accuracy: {p['accuracy']:.1f}% (observed in {p['frequency']} debates)\n"
                f"   - Condition: {p['condition']}\n"
            )
        
        return summary