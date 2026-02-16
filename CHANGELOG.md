# Changelog

All notable changes to the Agentic Mortgage Research Agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] - 2026-02-15

### 🎨 UX & Mobile Improvements

#### Added
- **Enhanced Sidebar Toggle Visibility**: Gradient-styled button with box shadows, borders, and enhanced mobile touch targets (18px padding)
- **Button Tooltips**: Hover tooltips on disabled Round 2/3 buttons prompting users to start the debate
- **Centered Button Captions**: Process flow explanation centered below "Start Debate" button
- **Session Persistence Messages**: Helpful info message when debate section unavailable after redeployment
- **GitHub Actions Keep-Alive Workflow**: Automated pinging every 5 minutes to prevent Streamlit Cloud sleep mode

#### Changed
- **Button Text Evolution**: "Continue to Full Debate" → "Start Debate" with clear caption explaining Rounds 2 & 3 execution
- **Error Messaging**: Inline warnings instead of full-page blocking blue screens during LLM cooldown
- **CSS Specificity**: Tightened selectors to only target sidebar toggle (removed unintended borders on share/star/edit/github buttons)
- **Icon Rendering**: Replaced 🔄 (device-dependent) with ⚙️ (universal) for system operations
- **Diagnostics Panel**: Simplified from 50+ lines to 20 lines showing only essential health checks

#### Removed
- **Confusing Role Names**: Eliminated "Data Collector", "Senior Analyst", "Multi-Agent" labels in logs
- **Excessive CSS Styling**: Removed gradient/border styling from header buttons except sidebar toggle
- **Verbose Diagnostics**: Removed secrets_path, cwd, running_in_cloud, and other internal details

### 📚 Documentation

#### Added
- **CHANGELOG.md**: Complete version history tracking
- **README.md v1.3.1 Section**: Comprehensive what's new guide with migration notes

#### Changed
- **Sidebar Version**: Updated to "v1.3.1 - UX & Infrastructure Hardening"
- **Tech Stack Section**: Added mobile CSS enhancements and GitHub Actions
- **System Design Notes**: Added mobile optimization, session persistence, and infrastructure details

---

## [1.3.0] - 2026-02-XX

### 🤖 Multi-Agent Debate System

#### Added
- **3-Round Debate System**: Initial Positions → Cross-Examination → Consensus Building
- **Agent Specialization**: Three distinct roles (📊 Planner, 📉 Market Analyst, 🛡️ Risk Officer)
- **Unified 3-Column Layout**: Side-by-side agent comparison across all rounds
- **Round Selection Buttons**: Toggle between Round 1/2/3 views while maintaining layout
- **Agent-Specific Color Themes**: Blue (Planner), Green (Market Analyst), Red (Risk Officer)
- **Automatic Round 1 Generation**: Initial positions created on "Agentic Plan" execution
- **Progressive Disclosure**: "Continue to Full Debate" button triggers Rounds 2 & 3 on demand
- **Voting System**: BULLISH/BEARISH/NEUTRAL stances with confidence percentages
- **Consensus Calculation**: Majority vote determines final recommendation

### 📊 Historical Learning

#### Added
- **SQLite Database Storage**: Complete debate history with timestamps
- **Outcome Validation**: Track prediction accuracy against actual market movements
- **Debate Retrieval**: View past debates with validation status
- **Audit Trail**: Full record of agent reasoning for every debate

### 🎨 UI/UX Enhancements

#### Added
- **Markdown-to-HTML Rendering**: Rich formatting in debate cards (bold, bullets, emphasis)
- **Color-Coded Debate Cards**: Agent-specific backgrounds with border accents
- **Confidence Indicators**: Visual display of agent certainty levels
- **Status Emojis**: 🟢 BULLISH, 🔴 BEARISH, 🟡 NEUTRAL stance indicators
- **Compact Layout**: Optimized spacing removes unnecessary dividers

#### Changed
- **Executive Summary**: Moved below debate for better context flow
- **Recommendation Display**: Positioned at bottom after full debate

---

## [1.2.0] - 2026-01-XX

### 🧠 LLM-Driven Planning

#### Added
- **Claude 3.5 Integration**: Anthropic API for intelligent decision-making
- **Agentic Planning**: LLM decides which actions to execute based on knowledge state
- **LLM-Based Insights**: Claude analyzes data trends and generates actionable insights
- **Cost Tracking**: Real-time session cost monitoring (~$0.002-0.003 per call)
- **Heuristic Fallback**: Rule-based planning when LLM unavailable

#### Changed
- **Planning Logic**: From static action sequences to dynamic LLM-driven decisions
- **Insight Generation**: From template-based to fully LLM-generated analysis

---

## [1.1.0] - 2026-01-XX

### 📈 Data Visualization

#### Added
- **Altair Charts**: Interactive mortgage rate and home price visualizations
- **Combined View**: Normalized rates vs. prices on single chart
- **Tooltip Interactions**: Hover details on chart data points

### 🎯 UI Improvements

#### Added
- **Real-Time Logging**: Emoji-tagged role execution tracking
- **Log Filtering**: Three-way filter (All logs, LLM decisions, Role outputs)
- **Agent Controls**: Sidebar controls for plan execution and summary regeneration
- **Status Indicators**: Spinner states during long-running operations

---

## [1.0.0] - 2025-12-XX

### 🎉 Initial Release

#### Added
- **Core Agent Architecture**: Knowledge base, action orchestration, logging
- **FRED API Integration**: Fetch 30-year fixed mortgage rates
- **Home Price Data**: FHFA Home Price Index retrieval
- **Data Analysis**: Trend detection, correlation analysis
- **Streamlit Dashboard**: Interactive UI with sidebar navigation
- **Configuration Management**: Environment variables, secrets.toml support
- **Documentation**: README.md with quickstart guide

#### Features
- Fetch mortgage rate data with timestamp caching
- Analyze rate trends (12-month average, latest rate)
- Fetch home price data when significant rate changes detected
- Correlate rates and home prices
- Generate basic insights summary
- Display data visualizations (line charts)
- Log decision trace with timestamps

---

## Version History Summary

- **v1.3.1** (Current): UX & Infrastructure Hardening
- **v1.3.0**: Multi-Agent Debate System with Historical Learning
- **v1.2.0**: LLM-Driven Planning & Insights
- **v1.1.0**: Data Visualization & UI Improvements
- **v1.0.0**: Initial Release with Core Agent Architecture

---

## Upgrade Path

### From v1.3.0 to v1.3.1
No breaking changes. Simply pull latest code. Optionally enable GitHub Actions keep-alive workflow by manually triggering it once.

### From v1.2.0 to v1.3.0
No breaking changes. Existing knowledge base structure preserved. SQLite database auto-created on first debate.

### From v1.1.0 to v1.2.0
No breaking changes. Add `ANTHROPIC_API_KEY` to secrets.toml or environment variables. System falls back to heuristic planning if key not provided.

### From v1.0.0 to v1.1.0
No breaking changes. Pure additive enhancements.

---

## Contributors

- **obizues** - Initial work and all version releases

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
