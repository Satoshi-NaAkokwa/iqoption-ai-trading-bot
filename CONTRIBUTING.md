# Contributing to IQ Option AI Trading Bot

Thank you for your interest in contributing to the IQ Option AI Trading Bot! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that the problem has already been reported or resolved.

When creating a bug report, please include:

- **Clear title and description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots or logs** if applicable
- **Environment details**:
  - Python version
  - IQ Option API version
  - Operating system
  - Bot version (v1-v6)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear description** of the enhancement
- **Use cases** and **benefits**
- **Potential implementation** ideas (if you have them)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Commit your changes** with clear messages
6. **Push to your fork** and create a Pull Request

## Code Style Guidelines

### Python Code Style

- Follow **PEP 8** guidelines
- Use **4 spaces** for indentation (not tabs)
- Maximum line length: **100 characters**
- Use meaningful variable and function names
- Add docstrings to functions and classes

#### Example:

```python
class MyAnalyzer:
    """Analyzes market data for trading signals."""

    def analyze_signal(self, candles: List[Dict]) -> Optional[Dict]:
        """
        Analyze candle data and generate trading signals.

        Args:
            candles: List of candlestick data

        Returns:
            Trading signal dict or None if no signal
        """
        # Implementation here
        pass
```

### Documentation

- Update README.md if you add new features
- Update CHANGELOG.md with version changes
- Add inline comments for complex logic
- Update config.py for new configuration options

### Testing

- Test your changes on demo accounts first
- Verify no breaking changes to existing features
- Check for any edge cases or error conditions
- Test with different market conditions

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add multi-timeframe analysis for v6 bot
fix: Correct RSI calculation in technical analyzer
docs: Update installation instructions
refactor: Simplify risk manager logic
test: Add unit tests for strategy engine
```

## Bot Version Guidelines

When creating or modifying bot versions:

### Version Naming

- Use descriptive names: `bot_market_adaptive_v6.py`
- Increment version number for major changes
- Maintain backward compatibility when possible

### Testing New Versions

1. Start with demo account testing
2. Test for at least 24 hours
3. Monitor win rate and performance
4. Document any issues or improvements
5. Get code review before merging to main

### Version Documentation

- Update README.md with new version details
- Add entry to CHANGELOG.md
- Document any breaking changes
- Update configuration examples

## Areas for Contribution

We welcome contributions in these areas:

- **Technical Indicators**: Add new technical analysis indicators
- **Trading Strategies**: Implement new trading strategies
- **LLM Integration**: Improve AI-powered analysis
- **Risk Management**: Enhance risk controls
- **Performance**: Optimize code for better performance
- **Testing**: Add unit tests and integration tests
- **Documentation**: Improve docs and examples
- **Bug Fixes**: Fix reported issues

## Development Workflow

1. **Set up your environment**:
   ```bash
   git clone https://github.com/your-username/iqoption-ai-trading-bot.git
   cd iqoption-ai-trading-bot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the guidelines above

4. **Test thoroughly**:
   ```bash
   # Run bot in test mode
   python bot_market_adaptive_v6.py
   ```

5. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request** on GitHub

## Code Review Process

All pull requests go through code review:

- Automated checks (linting, tests)
- Manual review by maintainers
- Feedback and iteration if needed
- Approval before merge to main

## Questions or Need Help?

- Open an issue for questions
- Join discussions on existing issues
- Check existing documentation first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the IQ Option AI Trading Bot! 🚀