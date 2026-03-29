"""
My ET — Extended Pydantic schemas.

Drop these into app/models/schemas.py (add to the My ET section).
New additions:
  - PersonaType enum
  - InvestorContext, FounderContext, StudentContext, ExecutiveContext
  - ExtendedUserProfile  (replaces UserProfile for My ET)
  - EnrichedArticle      (article + AI-generated persona snippet)
  - BriefingResponse     (full personalized briefing)
  - DeepDiveRequest/Response
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ================================================================
# My ET — Persona Types
# ================================================================

class PersonaType(str, Enum):
    INVESTOR  = "investor"
    FOUNDER   = "founder"
    STUDENT   = "student"
    EXECUTIVE = "executive"


# ── Per-persona context models ────────────────────────────────────

class InvestorContext(BaseModel):
    """Context fields for a retail investor persona."""
    portfolio_sectors: list[str] = Field(
        default_factory=list,
        description="Sectors the user holds (e.g. ['banking', 'IT', 'pharma'])",
    )
    investment_style: str = Field(
        default="long-term",
        description="long-term | short-term | swing-trader | SIP",
    )
    risk_appetite: str = Field(
        default="moderate",
        description="conservative | moderate | aggressive",
    )
    tracked_stocks: list[str] = Field(
        default_factory=list,
        description="Specific stocks/MFs the user tracks (e.g. ['HDFC Bank', 'Nifty 50'])",
    )


class FounderContext(BaseModel):
    """Context fields for a startup founder persona."""
    startup_sector: str = Field(
        default="",
        description="Sector the startup operates in (e.g. 'fintech', 'edtech')",
    )
    stage: str = Field(
        default="early",
        description="idea | early | seed | series-a | series-b | growth",
    )
    fundraising_status: str = Field(
        default="not-raising",
        description="not-raising | actively-raising | closing-round",
    )
    competitors: list[str] = Field(
        default_factory=list,
        description="Competitor names to track (e.g. ['Zepto', 'Blinkit'])",
    )


class StudentContext(BaseModel):
    """Context fields for a student persona."""
    field_of_study: str = Field(
        default="",
        description="Subject area (e.g. 'MBA Finance', 'B.Com', 'Engineering')",
    )
    career_goal: str = Field(
        default="",
        description="Aspiration (e.g. 'investment banking', 'product management')",
    )
    knowledge_level: str = Field(
        default="beginner",
        description="beginner | intermediate | advanced",
    )


class ExecutiveContext(BaseModel):
    """Context fields for a corporate executive persona."""
    industry: str = Field(
        default="",
        description="Industry the executive works in (e.g. 'FMCG', 'manufacturing')",
    )
    function: str = Field(
        default="",
        description="Functional role (e.g. 'CFO', 'Strategy', 'Operations')",
    )
    company_size: str = Field(
        default="large",
        description="startup | mid-size | large | enterprise",
    )
    strategic_focus: list[str] = Field(
        default_factory=list,
        description="Strategic priorities (e.g. ['expansion', 'cost optimisation'])",
    )


# ── Extended User Profile ─────────────────────────────────────────

class ExtendedUserProfile(BaseModel):
    """
    Full user profile for My ET personalisation.
    Extends the base UserProfile with persona type and rich context.
    """
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(default="", description="Display name")
    persona_type: PersonaType = Field(..., description="User's primary persona")

    # Base interests (used for ChromaDB retrieval — same as original UserProfile)
    interests: list[str] = Field(
        default_factory=list,
        description="Topic interests for article retrieval",
    )
    preferred_categories: list[str] = Field(default_factory=list)

    # Persona-specific context (only one will be populated)
    investor_context:  Optional[InvestorContext]  = None
    founder_context:   Optional[FounderContext]   = None
    student_context:   Optional[StudentContext]   = None
    executive_context: Optional[ExecutiveContext] = None

    def get_context_summary(self) -> str:
        """
        Returns a plain-English summary of the user's context
        for injection into LLM prompts.
        """
        if self.persona_type == PersonaType.INVESTOR and self.investor_context:
            ctx = self.investor_context
            return (
                f"I am a retail investor with a {ctx.risk_appetite} risk appetite. "
                f"I invest in: {', '.join(ctx.portfolio_sectors) or 'diversified sectors'}. "
                f"My investment style is {ctx.investment_style}. "
                f"I track: {', '.join(ctx.tracked_stocks) or 'general market indices'}."
            )
        elif self.persona_type == PersonaType.FOUNDER and self.founder_context:
            ctx = self.founder_context
            return (
                f"I am a startup founder in the {ctx.startup_sector} space, "
                f"at {ctx.stage} stage. "
                f"Fundraising status: {ctx.fundraising_status}. "
                f"Key competitors I watch: {', '.join(ctx.competitors) or 'none specified'}."
            )
        elif self.persona_type == PersonaType.STUDENT and self.student_context:
            ctx = self.student_context
            return (
                f"I am a {ctx.knowledge_level}-level student studying {ctx.field_of_study}. "
                f"My career goal is {ctx.career_goal}. "
                f"I need news explained clearly with context."
            )
        elif self.persona_type == PersonaType.EXECUTIVE and self.executive_context:
            ctx = self.executive_context
            return (
                f"I am a {ctx.function} executive in the {ctx.industry} industry "
                f"at a {ctx.company_size} company. "
                f"My strategic priorities: {', '.join(ctx.strategic_focus) or 'general business growth'}."
            )
        return "I am a business professional interested in Indian markets."


# ================================================================
# My ET — AI-Enriched Article Models
# ================================================================

class EnrichedArticle(BaseModel):
    """A news article enriched with a persona-aware AI snippet."""

    # Original article fields
    title: str
    summary: str
    link: str
    published: str
    source: str
    category: str = "general"

    # AI-generated fields
    persona_snippet: str = Field(
        default="",
        description="1-2 sentence 'what this means for you' insight, persona-aware",
    )
    relevance_score: float = Field(
        default=0.0,
        description="How relevant this article is to the user (0-1)",
    )
    sentiment: str = Field(
        default="neutral",
        description="positive | negative | neutral",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Auto-detected topic tags",
    )
    snippet_ready: bool = Field(
        default=False,
        description="Whether the AI snippet has been generated",
    )


class BriefingResponse(BaseModel):
    """Full personalized briefing for a user."""
    user_id: str
    persona_type: str
    articles: list[EnrichedArticle]
    total_articles: int
    enriched_count: int  # how many have AI snippets
    generated_at: str


# ================================================================
# My ET — Deep Dive
# ================================================================

class DeepDiveRequest(BaseModel):
    """Request for a full contextual breakdown of one article."""
    user_id: str
    article_title: str
    article_summary: str
    article_link: str = ""


class DeepDiveSection(BaseModel):
    """One section of the deep dive breakdown."""
    heading: str
    content: str


class DeepDiveResponse(BaseModel):
    """Full contextual breakdown of an article for a specific persona."""
    article_title: str
    persona_type: str
    sections: list[DeepDiveSection]
    bottom_line: str = Field(
        description="One sentence: the single most important takeaway for this persona"
    )
