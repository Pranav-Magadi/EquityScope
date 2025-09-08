# Real Estate Sector DCF Calculator
# Implements NAV-based valuation model for real estate companies

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RealEstateProject:
    """Individual real estate project details"""
    project_name: str
    location: str
    project_type: str  # Residential/Commercial/Mixed
    total_area_sqft: float
    saleable_area_sqft: float
    sold_area_sqft: float
    unsold_area_sqft: float
    avg_realization_per_sqft: float
    construction_cost_per_sqft: float
    completion_percentage: float
    expected_completion_months: int
    tier: str  # Tier 1/Tier 2/Tier 3 city

@dataclass
class RealEstateMetrics:
    """Real estate company financial metrics"""
    revenue: float
    ebitda: float
    net_profit: float
    total_debt: float
    net_debt: float
    cash_and_equivalents: float
    
    # Real estate specific metrics
    inventory_value: float          # Total inventory on books
    inventory_turnover: float       # Inventory turnover ratio
    debt_to_equity: float          # D/E ratio
    interest_coverage: float        # EBITDA/Interest
    
    # Project metrics
    projects: List[RealEstateProject]
    land_bank_area_sqft: float     # Total land bank
    land_bank_value: float         # Book value of land
    
    # Market metrics
    shares_outstanding: float
    current_price: float
    book_value_per_share: float

@dataclass
class NAVValuationResult:
    """Result of NAV-based real estate valuation"""
    gross_nav_per_share: float
    net_nav_per_share: float       # After debt adjustment
    project_nav: float             # Value from ongoing projects
    land_bank_nav: float           # Value from land bank
    discount_to_nav: float         # Current discount/premium to NAV
    nav_discount_rate: float       # Applied discount rate
    inventory_risk_adjustment: float
    method: str = "NAV_Based_Valuation"
    confidence: float = 0.0
    assumptions: Dict[str, float] = None

class RealEstateDCFCalculator:
    """
    Real Estate sector valuation using NAV-based approach
    
    Methodology:
    1. Project-wise NAV calculation
    2. Land bank valuation
    3. Debt adjustment
    4. Inventory risk assessment
    5. Location and tier-based adjustments
    """
    
    def __init__(self):
        # Real estate sector benchmarks
        self.sector_benchmarks = {
            "risk_free_rate": 0.065,
            "real_estate_risk_premium": 0.10,  # Higher risk premium
            "nav_discount_rate": 0.15,         # Discount rate for NAV
            "terminal_growth": 0.05,           # Real estate long-term growth
            "construction_risk_buffer": 0.10    # 10% cost overrun buffer
        }
        
        # Location-based pricing premiums
        self.location_premiums = {
            "tier_1": {
                "residential": 1.2,    # 20% premium
                "commercial": 1.3,     # 30% premium
                "mixed": 1.25
            },
            "tier_2": {
                "residential": 1.0,    # Base pricing
                "commercial": 1.1,     # 10% premium
                "mixed": 1.05
            },
            "tier_3": {
                "residential": 0.85,   # 15% discount
                "commercial": 0.9,     # 10% discount
                "mixed": 0.875
            }
        }
        
        # Risk adjustments
        self.risk_factors = {
            "high_debt_penalty": 0.20,         # D/E > 1.5
            "low_inventory_turnover": 0.15,    # Turnover < 0.3
            "construction_delay_risk": 0.10,   # Projects > 80% delayed
            "location_concentration": 0.05     # >70% in single location
        }
    
    async def calculate_nav_valuation(
        self, 
        ticker: str, 
        re_metrics: RealEstateMetrics,
        market_data: Dict = None
    ) -> NAVValuationResult:
        """
        Calculate NAV-based valuation for real estate company
        
        Args:
            ticker: Real estate company ticker
            re_metrics: Real estate specific metrics
            market_data: Market data including comparable transactions
        
        Returns:
            NAVValuationResult with NAV components
        """
        try:
            logger.info(f"Calculating NAV-based valuation for {ticker}")
            
            # Step 1: Calculate project-wise NAV
            project_nav = self._calculate_project_nav(re_metrics)
            
            # Step 2: Calculate land bank value
            land_bank_nav = self._calculate_land_bank_nav(re_metrics, market_data)
            
            # Step 3: Calculate gross NAV
            gross_nav = project_nav + land_bank_nav
            
            # Step 4: Apply debt adjustment
            net_nav = gross_nav - re_metrics.net_debt
            
            # Step 5: Apply risk adjustments
            risk_adjusted_nav, inventory_risk = self._apply_risk_adjustments(net_nav, re_metrics)
            
            # Step 6: Calculate per share values
            gross_nav_per_share = gross_nav / re_metrics.shares_outstanding
            net_nav_per_share = risk_adjusted_nav / re_metrics.shares_outstanding
            
            # Step 7: Calculate current discount to NAV
            discount_to_nav = (net_nav_per_share - re_metrics.current_price) / net_nav_per_share
            
            # Step 8: Calculate confidence score
            confidence = self._calculate_confidence_score(re_metrics)
            
            # Prepare assumptions
            assumptions = {
                "nav_discount_rate": self.sector_benchmarks["nav_discount_rate"],
                "construction_risk_buffer": self.sector_benchmarks["construction_risk_buffer"],
                "project_nav_million": project_nav / 1e6,
                "land_bank_nav_million": land_bank_nav / 1e6,
                "total_debt_million": re_metrics.total_debt / 1e6,
                "inventory_risk_adjustment": inventory_risk
            }
            
            result = NAVValuationResult(
                gross_nav_per_share=gross_nav_per_share,
                net_nav_per_share=net_nav_per_share,
                project_nav=project_nav,
                land_bank_nav=land_bank_nav,
                discount_to_nav=discount_to_nav,
                nav_discount_rate=self.sector_benchmarks["nav_discount_rate"],
                inventory_risk_adjustment=inventory_risk,
                confidence=confidence,
                assumptions=assumptions
            )
            
            logger.info(f"NAV calculation completed for {ticker}: Net NAV = ₹{net_nav_per_share:.2f}/share")
            return result
            
        except Exception as e:
            logger.error(f"Error in real estate NAV calculation for {ticker}: {e}")
            raise
    
    def _calculate_project_nav(self, metrics: RealEstateMetrics) -> float:
        """Calculate NAV from ongoing and planned projects"""
        
        total_project_nav = 0.0
        
        for project in metrics.projects:
            project_nav = self._calculate_individual_project_nav(project)
            total_project_nav += project_nav
            
            logger.debug(f"Project {project.project_name}: NAV = ₹{project_nav/1e6:.1f}M")
        
        return total_project_nav
    
    def _calculate_individual_project_nav(self, project: RealEstateProject) -> float:
        """Calculate NAV for individual project"""
        
        # Get location and type premium
        tier_key = project.tier.lower().replace(" ", "_")
        type_key = project.project_type.lower()
        
        location_premium = self.location_premiums.get(tier_key, {}).get(type_key, 1.0)
        
        # Calculate project revenue potential
        total_revenue = project.saleable_area_sqft * project.avg_realization_per_sqft * location_premium
        
        # Calculate project costs
        construction_cost = project.total_area_sqft * project.construction_cost_per_sqft
        # Add construction risk buffer
        total_cost = construction_cost * (1 + self.sector_benchmarks["construction_risk_buffer"])
        
        # Calculate gross project margin
        gross_margin = total_revenue - total_cost
        
        # Apply completion-based discount
        completion_factor = self._calculate_completion_discount(project)
        
        # Apply time value discount
        time_discount = self._calculate_time_discount(project.expected_completion_months)
        
        # Calculate project NAV
        project_nav = gross_margin * completion_factor * time_discount
        
        # Ensure non-negative NAV
        return max(project_nav, 0)
    
    def _calculate_completion_discount(self, project: RealEstateProject) -> float:
        """Calculate discount factor based on project completion status"""
        
        completion_pct = project.completion_percentage
        
        if completion_pct >= 0.90:  # >90% complete
            return 0.95
        elif completion_pct >= 0.70:  # 70-90% complete
            return 0.85
        elif completion_pct >= 0.50:  # 50-70% complete
            return 0.75
        elif completion_pct >= 0.30:  # 30-50% complete
            return 0.65
        else:  # <30% complete
            return 0.50
    
    def _calculate_time_discount(self, months_to_completion: int) -> float:
        """Calculate time value discount based on completion timeline"""
        
        if months_to_completion <= 12:  # Within 1 year
            return 0.95
        elif months_to_completion <= 24:  # 1-2 years
            return 0.85
        elif months_to_completion <= 36:  # 2-3 years
            return 0.75
        else:  # >3 years
            return 0.60
    
    def _calculate_land_bank_nav(self, metrics: RealEstateMetrics, market_data: Dict = None) -> float:
        """Calculate NAV from land bank holdings"""
        
        # Base land bank value from books
        base_land_value = metrics.land_bank_value
        
        # Apply market appreciation (if market data available)
        if market_data and "land_appreciation_rate" in market_data:
            appreciation_rate = market_data["land_appreciation_rate"]
            market_adjusted_value = base_land_value * (1 + appreciation_rate)
        else:
            # Use conservative 5% annual appreciation
            market_adjusted_value = base_land_value * 1.05
        
        # Apply development potential premium
        development_premium = self._calculate_development_premium(metrics)
        
        land_bank_nav = market_adjusted_value * (1 + development_premium)
        
        return land_bank_nav
    
    def _calculate_development_premium(self, metrics: RealEstateMetrics) -> float:
        """Calculate development potential premium for land bank"""
        
        # Base premium for developable land
        base_premium = 0.15  # 15% premium
        
        # Adjust based on inventory turnover (faster turnover = better execution)
        if metrics.inventory_turnover > 0.5:
            base_premium += 0.05
        elif metrics.inventory_turnover < 0.2:
            base_premium -= 0.10
        
        # Adjust based on debt levels (high debt reduces flexibility)
        if metrics.debt_to_equity > 1.5:
            base_premium -= 0.10
        elif metrics.debt_to_equity < 0.5:
            base_premium += 0.05
        
        return max(base_premium, 0.0)
    
    def _apply_risk_adjustments(self, base_nav: float, metrics: RealEstateMetrics) -> Tuple[float, float]:
        """Apply real estate specific risk adjustments"""
        
        total_risk_discount = 0.0
        
        # High debt penalty
        if metrics.debt_to_equity > 1.5:
            debt_penalty = min((metrics.debt_to_equity - 1.5) * 0.1, self.risk_factors["high_debt_penalty"])
            total_risk_discount += debt_penalty
        
        # Low inventory turnover penalty
        if metrics.inventory_turnover < 0.3:
            turnover_penalty = self.risk_factors["low_inventory_turnover"] * (0.3 - metrics.inventory_turnover)
            total_risk_discount += turnover_penalty
        
        # Construction and execution risk
        delayed_projects = sum(1 for p in metrics.projects if p.expected_completion_months > 36)
        if delayed_projects > len(metrics.projects) * 0.3:  # >30% projects delayed
            total_risk_discount += self.risk_factors["construction_delay_risk"]
        
        # Location concentration risk
        location_concentration = self._calculate_location_concentration(metrics.projects)
        if location_concentration > 0.70:  # >70% in single location
            total_risk_discount += self.risk_factors["location_concentration"]
        
        # Cap total discount at 40%
        total_risk_discount = min(total_risk_discount, 0.40)
        
        risk_adjusted_nav = base_nav * (1 - total_risk_discount)
        
        return risk_adjusted_nav, total_risk_discount
    
    def _calculate_location_concentration(self, projects: List[RealEstateProject]) -> float:
        """Calculate concentration risk by location"""
        
        if not projects:
            return 0.0
        
        location_counts = {}
        for project in projects:
            location = project.location
            location_counts[location] = location_counts.get(location, 0) + 1
        
        max_concentration = max(location_counts.values()) / len(projects)
        return max_concentration
    
    def _calculate_confidence_score(self, metrics: RealEstateMetrics) -> float:
        """Calculate confidence score based on real estate metrics"""
        
        confidence = 0.5  # Base confidence
        
        # Debt management
        if metrics.debt_to_equity < 1.0:
            confidence += 0.15
        elif metrics.debt_to_equity > 2.0:
            confidence -= 0.25
        
        # Inventory management
        if metrics.inventory_turnover > 0.5:
            confidence += 0.15
        elif metrics.inventory_turnover < 0.2:
            confidence -= 0.20
        
        # Interest coverage
        if metrics.interest_coverage > 3.0:
            confidence += 0.10
        elif metrics.interest_coverage < 1.5:
            confidence -= 0.15
        
        # Project diversification
        if len(metrics.projects) > 5:
            confidence += 0.05
        elif len(metrics.projects) < 2:
            confidence -= 0.10
        
        # Location diversification
        location_concentration = self._calculate_location_concentration(metrics.projects)
        if location_concentration < 0.50:
            confidence += 0.05
        elif location_concentration > 0.80:
            confidence -= 0.10
        
        return max(min(confidence, 0.85), 0.25)  # Cap between 25% and 85%

    def validate_realestate_inputs(self, metrics: RealEstateMetrics) -> Tuple[bool, str]:
        """Validate real estate metrics for reasonableness"""
        
        validations = [
            (metrics.revenue > 0, "Revenue must be positive"),
            (metrics.inventory_value > 0, "Inventory value must be positive"),
            (0 <= metrics.inventory_turnover <= 5.0, "Inventory turnover should be between 0 and 5"),
            (metrics.debt_to_equity >= 0, "D/E ratio cannot be negative"),
            (metrics.shares_outstanding > 0, "Shares outstanding must be positive"),
            (metrics.land_bank_area_sqft >= 0, "Land bank area cannot be negative"),
            (len(metrics.projects) > 0, "At least one project required for NAV calculation")
        ]
        
        for is_valid, error_msg in validations:
            if not is_valid:
                return False, error_msg
        
        # Validate individual projects
        for i, project in enumerate(metrics.projects):
            project_validations = [
                (project.total_area_sqft > 0, f"Project {i+1}: Total area must be positive"),
                (project.saleable_area_sqft <= project.total_area_sqft, f"Project {i+1}: Saleable area cannot exceed total area"),
                (0 <= project.completion_percentage <= 1.0, f"Project {i+1}: Completion % should be between 0 and 100%"),
                (project.avg_realization_per_sqft > 0, f"Project {i+1}: Realization per sqft must be positive"),
                (project.construction_cost_per_sqft > 0, f"Project {i+1}: Construction cost per sqft must be positive"),
                (project.tier.lower() in ["tier 1", "tier 2", "tier 3"], f"Project {i+1}: Tier must be 'Tier 1', 'Tier 2', or 'Tier 3'"),
                (project.project_type.lower() in ["residential", "commercial", "mixed"], f"Project {i+1}: Type must be 'Residential', 'Commercial', or 'Mixed'")
            ]
            
            for is_valid, error_msg in project_validations:
                if not is_valid:
                    return False, error_msg
        
        return True, "All validations passed"