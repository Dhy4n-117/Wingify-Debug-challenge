## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, read_financial_document

## Task 1: Verify the uploaded document
verification = Task(
    description=(
        "Verify that the uploaded document is a valid financial report.\n"
        "1. Read the document using the Financial Document Reader tool.\n"
        "2. Check if it contains standard financial components such as:\n"
        "   - Revenue/income figures\n"
        "   - Balance sheet data\n"
        "   - Cash flow information\n"
        "   - Quarterly or annual financial metrics\n"
        "3. Assess the document's data quality and completeness.\n"
        "4. Flag any anomalies, missing sections, or data integrity issues.\n"
        "5. Provide a clear verdict on whether this document is suitable for financial analysis."
    ),
    expected_output=(
        "A structured verification report containing:\n"
        "- Document type classification (e.g., 10-Q, 10-K, earnings report, investor update)\n"
        "- Identified financial components and their completeness\n"
        "- Data quality assessment (High/Medium/Low)\n"
        "- Any flagged issues or concerns\n"
        "- Final verdict: APPROVED or NEEDS REVIEW with justification"
    ),
    agent=verifier,
    tools=[read_financial_document],
    async_execution=False,
)

## Task 2: Analyze the financial document based on user query
analyze_financial_document = Task(
    description=(
        "Perform a comprehensive financial analysis based on the user's query: {query}\n\n"
        "Steps:\n"
        "1. Read the financial document thoroughly using the Financial Document Reader tool.\n"
        "2. Extract key financial metrics: revenue, net income, EPS, margins, cash flow, debt levels.\n"
        "3. Identify significant trends, YoY/QoQ changes, and notable patterns.\n"
        "4. Search the internet for relevant market context, industry benchmarks, and recent news.\n"
        "5. Synthesize findings into a clear, data-driven analysis that directly addresses the user's query.\n\n"
        "Important: Always cite specific numbers and data points from the document. "
        "Clearly distinguish between facts from the document and your analytical interpretations."
    ),
    expected_output=(
        "A comprehensive financial analysis report with:\n"
        "- Executive Summary: Key findings in 2-3 sentences\n"
        "- Financial Metrics Overview: Revenue, profit margins, EPS, cash flow with actual figures\n"
        "- Trend Analysis: Quarter-over-quarter and year-over-year comparisons\n"
        "- Market Context: How the company compares to industry peers and current market conditions\n"
        "- Key Observations: Notable strengths, weaknesses, opportunities, and threats\n"
        "- Data Sources: References to specific pages/sections of the document analyzed"
    ),
    agent=financial_analyst,
    tools=[read_financial_document, search_tool],
    async_execution=False,
)

## Task 3: Investment analysis and recommendations
investment_analysis = Task(
    description=(
        "Based on the financial analysis results, provide investment recommendations.\n\n"
        "User's original query: {query}\n\n"
        "Steps:\n"
        "1. Review the financial analysis findings from the previous task.\n"
        "2. Evaluate the company's investment potential based on fundamentals.\n"
        "3. Consider valuation metrics (P/E, P/B, EV/EBITDA) relative to peers.\n"
        "4. Search for recent analyst ratings, price targets, and market sentiment.\n"
        "5. Formulate balanced investment recommendations with clear rationale.\n\n"
        "Important: Always include risk disclaimers. Never guarantee returns. "
        "Recommendations should be appropriate for different investor profiles."
    ),
    expected_output=(
        "A structured investment recommendation report:\n"
        "- Investment Thesis: Clear bull/bear case summary\n"
        "- Valuation Assessment: Current valuation relative to fundamentals and peers\n"
        "- Recommendation: Buy/Hold/Sell with confidence level and rationale\n"
        "- Target Scenarios: Bull case, base case, and bear case with reasoning\n"
        "- Suitability: Which investor profiles this investment suits\n"
        "- Disclaimer: Standard investment risk disclaimer"
    ),
    agent=investment_advisor,
    tools=[read_financial_document, search_tool],
    async_execution=False,
)

## Task 4: Risk assessment
risk_assessment = Task(
    description=(
        "Conduct a comprehensive risk assessment based on the financial document analysis.\n\n"
        "User's original query: {query}\n\n"
        "Steps:\n"
        "1. Identify key risk factors from the financial document (debt levels, revenue concentration, etc.).\n"
        "2. Evaluate market risks: sector volatility, macroeconomic factors, competitive threats.\n"
        "3. Assess operational risks: management quality, regulatory exposure, supply chain dependencies.\n"
        "4. Search for recent risk-related news, regulatory actions, or industry headwinds.\n"
        "5. Quantify risks where possible and provide mitigation strategies.\n\n"
        "Important: Be balanced — identify both risks and mitigating factors. "
        "Use established risk frameworks rather than speculative assessments."
    ),
    expected_output=(
        "A structured risk assessment report:\n"
        "- Risk Summary: Overall risk rating (Low/Medium/High) with justification\n"
        "- Financial Risks: Liquidity, solvency, credit risk analysis with specific metrics\n"
        "- Market Risks: Sector, macro, and competitive risk factors\n"
        "- Operational Risks: Management, regulatory, and operational risk factors\n"
        "- Risk Mitigation: Recommended strategies to manage identified risks\n"
        "- Risk Matrix: Summary table of risks with likelihood and impact ratings"
    ),
    agent=risk_assessor,
    tools=[read_financial_document, search_tool],
    async_execution=False,
)