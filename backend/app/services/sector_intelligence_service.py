# Sector Intelligence Service
# Provides sector-specific assumptions from Aswath Damodaran's datasets
# Handles WACC calculation, terminal growth rates, and industry multiples

import json
import logging
import asyncio
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import aiohttp
from datetime import datetime, timedelta

from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

@dataclass
class SectorIntelligenceData:
    """Sector-specific intelligence from Damodaran datasets"""
    sector_name: str
    damodaran_name: str
    unlevered_beta: float
    levered_beta: float
    effective_tax_rate: float
    terminal_growth_rate: float
    typical_debt_equity_ratio: float
    industry_multiples: Dict[str, float]

@dataclass
class WACCComponents:
    """Components for WACC calculation"""
    risk_free_rate: float
    equity_risk_premium: float
    country_risk_premium: float
    unlevered_beta: float
    effective_tax_rate: float
    debt_equity_ratio: float

class SectorIntelligenceService:
    """
    Service for sector-specific assumptions using Damodaran data
    
    MVP Implementation:
    - Reads from local JSON file with Damodaran sector data
    - Provides WACC components for DCF calculations  
    - Maps local sector names to Damodaran classifications
    - Fetches live risk-free rate from market data
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        self.sector_data: Optional[Dict] = None
        self.data_file_path = Path(__file__).parent.parent / "data" / "sector_intelligence.json"
        
        # Load sector data on initialization
        self._load_sector_data()
    
    def _load_sector_data(self) -> None:
        """Load sector intelligence data from JSON file"""
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                self.sector_data = json.load(f)
            logger.info(f"Loaded sector intelligence data for {len(self.sector_data.get('sectors', {}))} sectors")
        except Exception as e:
            logger.error(f"Error loading sector intelligence data: {e}")
            self.sector_data = None
    
    def get_sector_mapping(self, local_sector: str) -> Optional[str]:
        """
        Map local sector names to Damodaran sector classifications
        
        Args:
            local_sector: Local sector name (e.g., 'IT', 'BFSI', 'PHARMA')
            
        Returns:
            Damodaran sector name or None if not found
        """
        if not self.sector_data:
            return None
            
        for damodaran_sector, data in self.sector_data.get('sectors', {}).items():
            local_names = data.get('local_names', [])
            if local_sector.upper() in [name.upper() for name in local_names]:
                return damodaran_sector
        
        logger.warning(f"No Damodaran mapping found for sector: {local_sector}")
        return None
    
    def get_sector_intelligence(self, local_sector: str) -> Optional[SectorIntelligenceData]:
        """
        Get comprehensive sector intelligence data
        
        Args:
            local_sector: Local sector name (e.g., 'IT', 'BFSI')
            
        Returns:
            SectorIntelligenceData or None if sector not found
        """
        damodaran_sector = self.get_sector_mapping(local_sector)
        if not damodaran_sector or not self.sector_data:
            return None
        
        sector_info = self.sector_data['sectors'].get(damodaran_sector)
        if not sector_info:
            return None
        
        return SectorIntelligenceData(
            sector_name=local_sector,
            damodaran_name=damodaran_sector,
            unlevered_beta=sector_info.get('unlevered_beta', 1.0),
            levered_beta=sector_info.get('levered_beta', 1.1),
            effective_tax_rate=sector_info.get('effective_tax_rate', 0.25),
            terminal_growth_rate=sector_info.get('terminal_growth_rate', 0.03),
            typical_debt_equity_ratio=sector_info.get('typical_debt_equity_ratio', 0.3),
            industry_multiples=sector_info.get('industry_multiples', {})
        )
    
    async def get_risk_free_rate(self) -> float:
        """
        Get current Indian 10-year G-Sec yield as risk-free rate
        
        MVP Implementation: Uses fallback rate if live data unavailable
        
        Returns:
            Risk-free rate as decimal (e.g., 0.065 for 6.5%)
        """
        try:
            # Check cache first
            if self.use_cache:
                cached_rate = await self.cache_manager.get(
                    cache_type=CacheType.MARKET_DATA,
                    identifier="india_10y_gsec",
                    calculation_type="risk_free_rate"
                )
                if cached_rate:
                    logger.info(f"Using cached risk-free rate: {cached_rate}")
                    return float(cached_rate)
            
            # TODO: Implement live API call to fetch 10Y G-Sec yield
            # For MVP, using fallback rate from sector data
            fallback_rate = self.sector_data.get('risk_free_rate', {}).get('fallback_rate', 0.065)
            
            # Cache the result for 1 hour
            if self.use_cache:
                await self.cache_manager.set(
                    cache_type=CacheType.MARKET_DATA,
                    identifier="india_10y_gsec",
                    data=fallback_rate,
                    calculation_type="risk_free_rate",
                    ttl_hours=1
                )
            
            logger.info(f"Using fallback risk-free rate: {fallback_rate}")
            return fallback_rate
            
        except Exception as e:
            logger.error(f"Error fetching risk-free rate: {e}")
            return 0.065  # Default fallback
    
    async def calculate_wacc_components(
        self, 
        local_sector: str, 
        company_debt_equity_ratio: Optional[float] = None
    ) -> Optional[WACCComponents]:
        """
        Calculate WACC components for a sector
        
        Args:
            local_sector: Local sector name
            company_debt_equity_ratio: Company's actual D/E ratio, or None to use sector typical
            
        Returns:
            WACCComponents or None if sector not found
        """
        try:
            # Get sector intelligence
            sector_intel = self.get_sector_intelligence(local_sector)
            if not sector_intel:
                logger.warning(f"No sector intelligence found for {local_sector}")
                return None
            
            # Get India country data
            india_data = self.sector_data.get('india', {})
            
            # Get risk-free rate
            risk_free_rate = await self.get_risk_free_rate()
            
            # Use company D/E ratio if provided, otherwise use sector typical
            debt_equity_ratio = company_debt_equity_ratio or sector_intel.typical_debt_equity_ratio
            
            return WACCComponents(
                risk_free_rate=risk_free_rate,
                equity_risk_premium=india_data.get('equity_risk_premium', 0.085),
                country_risk_premium=india_data.get('country_risk_premium', 0.0485),
                unlevered_beta=sector_intel.unlevered_beta,
                effective_tax_rate=sector_intel.effective_tax_rate,
                debt_equity_ratio=debt_equity_ratio
            )
            
        except Exception as e:
            logger.error(f"Error calculating WACC components for {local_sector}: {e}")
            return None
    
    async def calculate_wacc(
        self, 
        local_sector: str, 
        company_debt_equity_ratio: Optional[float] = None
    ) -> float:
        """
        Calculate WACC for a sector using Damodaran methodology
        
        Formula:
        WACC = (E/V * Re) + (D/V * Rd * (1-Tc))
        Where:
        Re = Risk-free rate + Beta * (Equity Risk Premium + Country Risk Premium)
        Rd = Risk-free rate + Credit spread (simplified as risk-free + 2%)
        
        Args:
            local_sector: Local sector name
            company_debt_equity_ratio: Company's D/E ratio
            
        Returns:
            WACC as decimal (e.g., 0.12 for 12%)
        """
        try:
            components = await self.calculate_wacc_components(local_sector, company_debt_equity_ratio)
            if not components:
                logger.warning(f"Using fallback WACC for {local_sector}")
                return 0.12  # Fallback WACC
            
            # Calculate cost of equity (CAPM with country risk)
            total_risk_premium = components.equity_risk_premium + components.country_risk_premium
            cost_of_equity = components.risk_free_rate + (components.unlevered_beta * total_risk_premium)
            
            # Calculate cost of debt (simplified)
            cost_of_debt = components.risk_free_rate + 0.02  # 2% credit spread
            after_tax_cost_of_debt = cost_of_debt * (1 - components.effective_tax_rate)
            
            # Calculate weights
            debt_weight = components.debt_equity_ratio / (1 + components.debt_equity_ratio)
            equity_weight = 1 / (1 + components.debt_equity_ratio)
            
            # Calculate WACC
            wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)
            
            # Sanity check
            wacc = max(0.08, min(0.20, wacc))  # Between 8% and 20%
            
            logger.info(f"Calculated WACC for {local_sector}: {wacc:.2%}")
            return wacc
            
        except Exception as e:
            logger.error(f"Error calculating WACC for {local_sector}: {e}")
            return 0.12  # Fallback WACC
    
    def get_industry_multiples(self, local_sector: str) -> Dict[str, float]:
        """
        Get industry multiples for valuation
        
        Args:
            local_sector: Local sector name
            
        Returns:
            Dictionary of industry multiples (PE, EV/EBITDA, P/B)
        """
        sector_intel = self.get_sector_intelligence(local_sector)
        if sector_intel:
            return sector_intel.industry_multiples
        
        # Fallback multiples
        return {
            "pe_ratio": 16.0,
            "ev_ebitda": 10.0,
            "price_to_book": 2.0
        }
    
    async def refresh_data(self) -> bool:
        """
        Refresh sector intelligence data
        
        Returns:
            True if data refreshed successfully
        """
        try:
            self._load_sector_data()
            
            # Clear related caches
            if self.use_cache:
                await self.cache_manager.invalidate(
                    cache_type=CacheType.MARKET_DATA,
                    identifier="india_10y_gsec"
                )
            
            logger.info("Sector intelligence data refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing sector intelligence data: {e}")
            return False
    
    def get_supported_sectors(self) -> List[str]:
        """
        Get list of supported local sector names
        
        Returns:
            List of supported sector names
        """
        if not self.sector_data:
            return []
        
        supported_sectors = []
        for sector_data in self.sector_data.get('sectors', {}).values():
            supported_sectors.extend(sector_data.get('local_names', []))
        
        return list(set(supported_sectors))  # Remove duplicates

# Global instance for use across the application
sector_intelligence_service = SectorIntelligenceService()