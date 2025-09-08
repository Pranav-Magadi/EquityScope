# Blended Multiples Service
# Implements professional blended valuation for multi-segment conglomerates
# Handles the complex valuation challenge described for companies like Reliance

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import yfinance as yf
import numpy as np

from .dynamic_sector_classification_service import DynamicSectorClassificationService, BusinessSegment, SectorCategory
from .peer_comparison_service import PeerComparisonService
from .intelligent_cache import intelligent_cache, CacheType

logger = logging.getLogger(__name__)

def _safe_enum_value(enum_obj) -> str:
    """Safely get enum value, handling both enum objects and strings"""
    try:
        if hasattr(enum_obj, 'value'):
            return enum_obj.value
        elif str(enum_obj).startswith('SectorCategory.'):
            # Handle string representation like 'SectorCategory.ENERGY'
            enum_name = str(enum_obj).replace('SectorCategory.', '')
            # Try to find the actual enum to get its value
            for sector in SectorCategory:
                if sector.name == enum_name:
                    return sector.value
            return enum_name
        else:
            return str(enum_obj)
    except Exception:
        return str(enum_obj)

@dataclass
class SectorMultiples:
    """Sector-specific valuation multiples"""
    sector: SectorCategory
    pe_ratio: float
    pb_ratio: float
    ev_ebitda: float
    ev_revenue: float
    roe_premium: float  # Premium/discount based on ROE vs sector average
    confidence_level: float  # 0-100, based on peer data quality

@dataclass
class SegmentValuation:
    """Individual segment valuation"""
    business_segment: BusinessSegment
    sector_multiples: SectorMultiples
    estimated_segment_value: float
    valuation_approach: str  # "PE", "EV/EBITDA", "EV/Revenue", "DCF"
    confidence_score: float

@dataclass
class BlendedValuationResult:
    """Complete blended valuation for multi-segment company"""
    ticker: str
    company_name: str
    is_conglomerate: bool
    
    # Individual segment valuations
    segment_valuations: List[SegmentValuation]
    
    # Blended results
    blended_pe_multiple: float
    blended_ev_ebitda_multiple: float
    pure_play_discount: float  # Conglomerate discount (typically 10-20%)
    
    # Final valuation
    sum_of_parts_value: float
    discounted_sotp_value: float  # After applying conglomerate discount
    current_market_value: float
    valuation_gap: float  # Percentage over/under-valued
    
    # Quality metrics
    valuation_confidence: float  # Weighted average of segment confidences
    data_warnings: List[str]
    methodology_notes: List[str]
    
    # Meta
    analysis_date: datetime
    last_updated: datetime

class BlendedMultiplesService:
    """
    Blended Multiples Service for Conglomerate Valuation
    
    Implements the professional approach for valuing multi-segment companies:
    1. Identify business segments and their revenue contributions
    2. Find appropriate sector multiples for each segment
    3. Calculate weighted-average blended multiples
    4. Apply conglomerate discount
    5. Compare to current market valuation
    
    This solves the "averaging apples and oranges" problem you described.
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache_manager = intelligent_cache
        
        # Initialize required services
        self.sector_classification_service = DynamicSectorClassificationService()
        self.peer_comparison_service = PeerComparisonService()
        
        # Professional valuation parameters
        self.conglomerate_discount_rates = {
            'large_cap': 0.15,      # 15% discount for large diversified companies
            'mid_cap': 0.20,        # 20% discount for mid-cap conglomerates  
            'small_cap': 0.25       # 25% discount for small diversified companies
        }
        
        # Sector multiple preferences (which multiple works best for each sector)
        self.sector_multiple_preferences = {
            SectorCategory.BFSI: {'primary': 'pb_ratio', 'secondary': 'pe_ratio'},
            SectorCategory.IT: {'primary': 'pe_ratio', 'secondary': 'ev_revenue'},
            SectorCategory.PHARMA: {'primary': 'pe_ratio', 'secondary': 'ev_ebitda'},
            SectorCategory.FMCG: {'primary': 'pe_ratio', 'secondary': 'ev_ebitda'},
            SectorCategory.AUTO: {'primary': 'pe_ratio', 'secondary': 'ev_ebitda'},
            SectorCategory.ENERGY: {'primary': 'ev_ebitda', 'secondary': 'pe_ratio'},
            SectorCategory.TELECOM: {'primary': 'ev_ebitda', 'secondary': 'ev_revenue'},
            SectorCategory.REALESTATE: {'primary': 'pb_ratio', 'secondary': 'pe_ratio'}
        }
    
    async def calculate_blended_valuation(
        self,
        ticker: str,
        force_refresh: bool = False
    ) -> BlendedValuationResult:
        """
        Calculate comprehensive blended valuation for multi-segment company
        
        Args:
            ticker: Stock ticker (e.g., 'RELIANCE.NS')
            force_refresh: Skip cache and recalculate
            
        Returns:
            BlendedValuationResult with segment-wise and blended valuations
        """
        try:
            logger.info(f"Starting blended valuation analysis for {ticker}")
            
            # Check cache first
            if self.use_cache and not force_refresh:
                cached_result = await self.cache_manager.get(
                    CacheType.FINANCIAL_DATA, f"{ticker}_blended_valuation"
                )
                if cached_result:
                    logger.info(f"Cache hit for {ticker} blended valuation - reconstructing objects")
                    # Reconstruct objects from cached dict
                    try:
                        return self._reconstruct_from_cache(cached_result)
                    except Exception as e:
                        logger.warning(f"Failed to reconstruct from cache for {ticker}: {e}, proceeding with fresh calculation")
            
            # Step 1: Get multi-segment classification (no peers needed for segment valuation)
            classification = await self.sector_classification_service.classify_company(
                ticker, include_peers=False
            )
            
            if not classification.is_conglomerate:
                logger.info(f"{ticker} is not a conglomerate, using single-sector valuation")
                return await self._single_sector_valuation(ticker, classification)
            
            # Step 2: Get sector multiples for each business segment
            segment_valuations = []
            methodology_notes = []
            data_warnings = []
            
            for segment in classification.business_segments:
                try:
                    sector_multiples = await self._get_sector_multiples(segment.sector)
                    segment_valuation = await self._value_business_segment(
                        ticker, segment, sector_multiples
                    )
                    segment_valuations.append(segment_valuation)
                    
                    sector_display = _safe_enum_value(segment.sector)
                    methodology_notes.append(
                        f"{sector_display}: {segment.estimated_revenue_contribution:.1f}% contribution, "
                        f"using {segment_valuation.valuation_approach} approach"
                    )
                    
                except Exception as e:
                    sector_display = _safe_enum_value(segment.sector)
                    logger.warning(f"Failed to value segment {sector_display} for {ticker}: {e}")
                    data_warnings.append(f"Segment valuation failed: {sector_display}")
            
            if not segment_valuations:
                raise ValueError(f"No segments could be valued for {ticker}")
            
            # Step 3: Calculate blended multiples
            blended_multiples = self._calculate_blended_multiples(segment_valuations)
            
            # Step 4: Calculate Sum-of-the-Parts value
            sotp_value = sum(sv.estimated_segment_value for sv in segment_valuations)
            
            # Step 5: Apply conglomerate discount
            discount_rate = self._determine_conglomerate_discount(classification.market_cap_category)
            discounted_value = sotp_value * (1 - discount_rate)
            
            # Step 6: Get current market value for comparison
            current_market_value = await self._get_current_market_value(ticker)
            valuation_gap = ((discounted_value - current_market_value) / current_market_value * 100) if current_market_value > 0 else 0
            
            # Step 7: Calculate confidence score
            confidence_score = np.mean([sv.confidence_score for sv in segment_valuations])
            
            # Create result
            result = BlendedValuationResult(
                ticker=ticker,
                company_name=classification.company_name,
                is_conglomerate=True,
                segment_valuations=segment_valuations,
                blended_pe_multiple=blended_multiples['pe_ratio'],
                blended_ev_ebitda_multiple=blended_multiples['ev_ebitda'],
                pure_play_discount=discount_rate * 100,
                sum_of_parts_value=sotp_value,
                discounted_sotp_value=discounted_value,
                current_market_value=current_market_value,
                valuation_gap=valuation_gap,
                valuation_confidence=confidence_score,
                data_warnings=data_warnings,
                methodology_notes=methodology_notes,
                analysis_date=datetime.now(),
                last_updated=datetime.now()
            )
            
            # Cache the result (with enum serialization)
            if self.use_cache:
                # Convert result to dict with proper enum handling
                result_dict = asdict(result)
                # Convert enum fields to strings for JSON serialization
                self._serialize_enums_in_dict(result_dict)
                
                await self.cache_manager.set(
                    CacheType.FINANCIAL_DATA,
                    f"{ticker}_blended_valuation",
                    result_dict
                )
            
            logger.info(
                f"Blended valuation completed for {ticker}: "
                f"SOTP ₹{sotp_value/1e12:.1f}T, Discounted ₹{discounted_value/1e12:.1f}T, "
                f"Gap: {valuation_gap:+.1f}%"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in blended valuation for {ticker}: {e}")
            raise
    
    async def _get_sector_multiples(self, sector) -> SectorMultiples:
        """Get sector-specific valuation multiples"""
        
        try:
            # Handle both enum and string inputs
            if hasattr(sector, 'name'):
                sector_name = sector.name
                sector_enum = sector
            else:
                # It's a string, convert to enum
                sector_name = sector
                # Find matching enum
                sector_enum = None
                for cat in SectorCategory:
                    if cat.name == sector or cat.value == sector:
                        sector_enum = cat
                        sector_name = cat.name
                        break
                if not sector_enum:
                    sector_enum = SectorCategory.GENERAL
                    sector_name = 'GENERAL'
            
            # Get sector benchmarks from peer comparison service
            sector_benchmarks = await self.peer_comparison_service.get_sector_financial_benchmarks(
                sector_name  # Use enum name (e.g., 'BFSI', 'IT')
            )
            
            if isinstance(sector_benchmarks, dict) and 'benchmarks' in sector_benchmarks:
                benchmarks = sector_benchmarks['benchmarks']
                
                # Extract multiples with fallbacks
                pe_ratio = benchmarks.get('pe_ratio', {}).get('median', 15.0)
                pb_ratio = benchmarks.get('pb_ratio', {}).get('median', 2.0)
                
                # Estimate EV multiples from available data
                ev_ebitda = pe_ratio * 0.7  # Rough approximation: EV/EBITDA ≈ PE * 0.7
                ev_revenue = pb_ratio * 1.5  # Rough approximation: EV/Revenue ≈ PB * 1.5
                
                # Calculate confidence based on data availability
                data_points = sum(1 for metric in benchmarks.values() if metric.get('count', 0) > 0)
                confidence = min(data_points * 25, 90)  # Max 90% confidence
                
                return SectorMultiples(
                    sector=sector_enum,
                    pe_ratio=pe_ratio,
                    pb_ratio=pb_ratio,
                    ev_ebitda=ev_ebitda,
                    ev_revenue=ev_revenue,
                    roe_premium=0.0,  # To be implemented with ROE analysis
                    confidence_level=confidence
                )
            
            else:
                # Fallback to industry standard multiples
                return self._get_fallback_multiples(sector_enum)
                
        except Exception as e:
            sector_display = _safe_enum_value(sector)
            logger.warning(f"Error getting sector multiples for {sector_display}: {e}")
            return self._get_fallback_multiples(sector_enum)
    
    def _get_fallback_multiples(self, sector: SectorCategory) -> SectorMultiples:
        """Fallback sector multiples when data is unavailable"""
        
        # Industry standard multiples (conservative estimates)
        fallback_multiples = {
            SectorCategory.BFSI: {'pe': 12, 'pb': 1.5, 'ev_ebitda': 8, 'ev_revenue': 2},
            SectorCategory.IT: {'pe': 20, 'pb': 4, 'ev_ebitda': 12, 'ev_revenue': 3},
            SectorCategory.PHARMA: {'pe': 18, 'pb': 3, 'ev_ebitda': 11, 'ev_revenue': 4},
            SectorCategory.FMCG: {'pe': 25, 'pb': 5, 'ev_ebitda': 15, 'ev_revenue': 2.5},
            SectorCategory.AUTO: {'pe': 15, 'pb': 2, 'ev_ebitda': 10, 'ev_revenue': 1.5},
            SectorCategory.ENERGY: {'pe': 10, 'pb': 1.2, 'ev_ebitda': 6, 'ev_revenue': 1},
            SectorCategory.TELECOM: {'pe': 16, 'pb': 2.5, 'ev_ebitda': 8, 'ev_revenue': 2},
            SectorCategory.CHEMICALS: {'pe': 14, 'pb': 2.2, 'ev_ebitda': 9, 'ev_revenue': 1.8},
            SectorCategory.REALESTATE: {'pe': 12, 'pb': 1.8, 'ev_ebitda': 10, 'ev_revenue': 3}
        }
        
        multiples = fallback_multiples.get(sector, {'pe': 15, 'pb': 2, 'ev_ebitda': 10, 'ev_revenue': 2})
        
        return SectorMultiples(
            sector=sector,
            pe_ratio=multiples['pe'],
            pb_ratio=multiples['pb'],
            ev_ebitda=multiples['ev_ebitda'],
            ev_revenue=multiples['ev_revenue'],
            roe_premium=0.0,
            confidence_level=40  # Lower confidence for fallback data
        )
    
    async def _value_business_segment(
        self,
        ticker: str,
        segment: BusinessSegment,
        sector_multiples: SectorMultiples
    ) -> SegmentValuation:
        """Value individual business segment"""
        
        try:
            # Get company financial data
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get total company metrics
            market_cap = info.get('marketCap', 0)
            revenue = info.get('totalRevenue', 0)
            ebitda = info.get('ebitda', 0)
            
            # Estimate segment-specific metrics based on contribution percentage
            segment_contribution = segment.estimated_revenue_contribution / 100
            estimated_segment_revenue = revenue * segment_contribution
            estimated_segment_ebitda = ebitda * segment_contribution
            
            # Handle sector field that might be string or enum
            if hasattr(segment.sector, 'name'):
                sector_key = segment.sector
            else:
                # Convert string to enum
                sector_key = None
                for cat in SectorCategory:
                    if cat.name == segment.sector or cat.value == segment.sector:
                        sector_key = cat
                        break
                if not sector_key:
                    sector_key = SectorCategory.GENERAL
            
            # Choose best valuation approach for this sector
            preferences = self.sector_multiple_preferences.get(
                sector_key, {'primary': 'pe_ratio', 'secondary': 'ev_ebitda'}
            )
            
            # Calculate segment value using preferred approach
            if preferences['primary'] == 'ev_revenue' and estimated_segment_revenue > 0:
                segment_value = estimated_segment_revenue * sector_multiples.ev_revenue
                approach = "EV/Revenue"
                confidence = sector_multiples.confidence_level * 0.8  # Revenue multiples less precise
                
            elif preferences['primary'] == 'ev_ebitda' and estimated_segment_ebitda > 0:
                segment_value = estimated_segment_ebitda * sector_multiples.ev_ebitda
                approach = "EV/EBITDA"
                confidence = sector_multiples.confidence_level * 0.9
                
            elif preferences['primary'] == 'pe_ratio':
                # For PE, need to estimate segment earnings
                net_margin = info.get('profitMargins', 0.1)  # Default 10% if not available
                estimated_segment_earnings = estimated_segment_revenue * net_margin
                segment_value = estimated_segment_earnings * sector_multiples.pe_ratio
                approach = "P/E Ratio"
                confidence = sector_multiples.confidence_level
                
            else:
                # Fallback to revenue multiple
                segment_value = estimated_segment_revenue * sector_multiples.ev_revenue
                approach = "EV/Revenue (Fallback)"
                confidence = 50  # Lower confidence for fallback
            
            # Apply segment-specific adjustments
            segment_value *= self._get_segment_quality_adjustment(segment)
            
            return SegmentValuation(
                business_segment=segment,
                sector_multiples=sector_multiples,
                estimated_segment_value=segment_value,
                valuation_approach=approach,
                confidence_score=confidence
            )
            
        except Exception as e:
            sector_display = getattr(segment.sector, 'value', str(segment.sector))
            logger.error(f"Error valuing segment {sector_display} for {ticker}: {e}")
            # Return minimal valuation to avoid complete failure
            return SegmentValuation(
                business_segment=segment,
                sector_multiples=sector_multiples,
                estimated_segment_value=0.0,
                valuation_approach="Failed",
                confidence_score=0.0
            )
    
    def _get_segment_quality_adjustment(self, segment: BusinessSegment) -> float:
        """Apply quality adjustments to segment valuations"""
        
        # Base adjustment is neutral
        adjustment = 1.0
        
        # Adjust based on segment confidence level
        if segment.confidence_level > 80:
            adjustment *= 1.0  # High confidence, no adjustment
        elif segment.confidence_level > 60:
            adjustment *= 0.95  # Slight conservative adjustment
        else:
            adjustment *= 0.90  # More conservative for low confidence
        
        # Adjust based on segment size (larger segments get slight premium)
        if segment.estimated_revenue_contribution > 40:
            adjustment *= 1.02  # 2% premium for major segments
        elif segment.estimated_revenue_contribution < 10:
            adjustment *= 0.95  # 5% discount for very small segments
        
        return adjustment
    
    def _calculate_blended_multiples(self, segment_valuations: List[SegmentValuation]) -> Dict[str, float]:
        """Calculate weighted-average blended multiples"""
        
        total_value = sum(sv.estimated_segment_value for sv in segment_valuations)
        
        if total_value == 0:
            return {'pe_ratio': 15.0, 'ev_ebitda': 10.0}  # Fallback multiples
        
        # Calculate weighted averages
        blended_pe = 0
        blended_ev_ebitda = 0
        
        for sv in segment_valuations:
            weight = sv.estimated_segment_value / total_value
            blended_pe += sv.sector_multiples.pe_ratio * weight
            blended_ev_ebitda += sv.sector_multiples.ev_ebitda * weight
        
        return {
            'pe_ratio': blended_pe,
            'ev_ebitda': blended_ev_ebitda
        }
    
    def _determine_conglomerate_discount(self, market_cap_category: str) -> float:
        """Determine appropriate conglomerate dicount rate"""
        
        category_lower = market_cap_category.lower()
        
        if 'large' in category_lower:
            return self.conglomerate_discount_rates['large_cap']
        elif 'mid' in category_lower:
            return self.conglomerate_discount_rates['mid_cap']
        else:
            return self.conglomerate_discount_rates['small_cap']
    
    async def _get_current_market_value(self, ticker: str) -> float:
        """Get current market capitalization"""
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('marketCap', 0)
            
        except Exception as e:
            logger.warning(f"Could not get market value for {ticker}: {e}")
            return 0
    
    async def _single_sector_valuation(
        self,
        ticker: str,
        classification
    ) -> BlendedValuationResult:
        """Handle single-sector companies (not conglomerates)"""
        
        # For single-sector companies, create a simple result
        current_market_value = await self._get_current_market_value(ticker)
        
        return BlendedValuationResult(
            ticker=ticker,
            company_name=classification.company_name,
            is_conglomerate=False,
            segment_valuations=[],
            blended_pe_multiple=0.0,
            blended_ev_ebitda_multiple=0.0,
            pure_play_discount=0.0,
            sum_of_parts_value=current_market_value,
            discounted_sotp_value=current_market_value,
            current_market_value=current_market_value,
            valuation_gap=0.0,
            valuation_confidence=50.0,
            data_warnings=["Company is not a conglomerate - single sector valuation recommended"],
            methodology_notes=["Single sector company - standard valuation methods recommended"],
            analysis_date=datetime.now(),
            last_updated=datetime.now()
        )
    
    def _serialize_enums_in_dict(self, data):
        """Recursively convert enums to strings in nested dictionaries and lists"""
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'name') and hasattr(value, 'value'):  # It's an enum
                    data[key] = value.name  # Use enum name (e.g., 'ENERGY')
                elif isinstance(value, (dict, list)):
                    self._serialize_enums_in_dict(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if hasattr(item, 'name') and hasattr(item, 'value'):  # It's an enum
                    data[i] = item.name  # Convert enum to name
                elif isinstance(item, (dict, list)):
                    self._serialize_enums_in_dict(item)
    
    def _reconstruct_from_cache(self, cached_data: Dict) -> BlendedValuationResult:
        """Reconstruct BlendedValuationResult from cached dictionary"""
        
        # Reconstruct segment valuations
        segment_valuations = []
        if 'segment_valuations' in cached_data:
            for seg_data in cached_data['segment_valuations']:
                # Reconstruct BusinessSegment
                bus_seg_data = seg_data['business_segment']
                
                # Convert sector string back to enum
                sector_enum = SectorCategory.GENERAL
                if isinstance(bus_seg_data['sector'], str):
                    for cat in SectorCategory:
                        if cat.name == bus_seg_data['sector']:
                            sector_enum = cat
                            break
                
                business_segment = BusinessSegment(
                    sector=sector_enum,
                    sub_industry=bus_seg_data['sub_industry'],
                    estimated_revenue_contribution=bus_seg_data['estimated_revenue_contribution'],
                    confidence_level=bus_seg_data['confidence_level'],
                    keywords_found=bus_seg_data['keywords_found']
                )
                
                # Reconstruct SectorMultiples
                mult_data = seg_data['sector_multiples']
                sector_multiples = SectorMultiples(
                    sector=sector_enum,
                    pe_ratio=mult_data['pe_ratio'],
                    pb_ratio=mult_data['pb_ratio'],
                    ev_ebitda=mult_data['ev_ebitda'],
                    ev_revenue=mult_data['ev_revenue'],
                    roe_premium=mult_data['roe_premium'],
                    confidence_level=mult_data['confidence_level']
                )
                
                # Reconstruct SegmentValuation
                segment_valuation = SegmentValuation(
                    business_segment=business_segment,
                    sector_multiples=sector_multiples,
                    estimated_segment_value=seg_data['estimated_segment_value'],
                    valuation_approach=seg_data['valuation_approach'],
                    confidence_score=seg_data['confidence_score']
                )
                
                segment_valuations.append(segment_valuation)
        
        # Reconstruct main result
        return BlendedValuationResult(
            ticker=cached_data['ticker'],
            company_name=cached_data['company_name'],
            is_conglomerate=cached_data['is_conglomerate'],
            segment_valuations=segment_valuations,
            blended_pe_multiple=cached_data['blended_pe_multiple'],
            blended_ev_ebitda_multiple=cached_data['blended_ev_ebitda_multiple'],
            pure_play_discount=cached_data['pure_play_discount'],
            sum_of_parts_value=cached_data['sum_of_parts_value'],
            discounted_sotp_value=cached_data['discounted_sotp_value'],
            current_market_value=cached_data['current_market_value'],
            valuation_gap=cached_data['valuation_gap'],
            valuation_confidence=cached_data['valuation_confidence'],
            data_warnings=cached_data['data_warnings'],
            methodology_notes=cached_data['methodology_notes'],
            analysis_date=datetime.fromisoformat(cached_data['analysis_date']) if isinstance(cached_data['analysis_date'], str) else cached_data['analysis_date'],
            last_updated=datetime.fromisoformat(cached_data['last_updated']) if isinstance(cached_data['last_updated'], str) else cached_data['last_updated']
        )