// Test suite for sector normalization utility functions
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFModelsCard } from '../components/DCFValuation/DCFModelsCard';
import type { SummaryResponse } from '../types/summary';

// Mock API Service to avoid actual API calls in tests
jest.mock('../services/api', () => ({
  getFinancialData: jest.fn(),
  getBasicCompanyData: jest.fn(),
  getDCFDefaults: jest.fn()
}));

// Create a minimal mock summary data for testing
const createMockSummaryData = (sector: string): SummaryResponse => ({
  ticker: 'TEST.NS',
  company_name: 'Test Company',
  fair_value_band: {
    min_value: 90,
    max_value: 110,
    current_price: 100,
    method: 'DCF',
    confidence: 0.75
  },
  investment_label: 'Neutral',
  key_factors: ['Test factor'],
  valuation_insights: 'Test insights',
  market_signals: 'Test signals',
  business_fundamentals: 'Test fundamentals',
  data_health_warnings: [],
  analysis_timestamp: '2025-07-31T14:00:00.000Z',
  analysis_mode: 'simple',
  sector
});

// Test sector normalization by rendering component and checking console logs
const testSectorNormalization = (inputSector: string, expectedNormalizedSector: string) => {
  const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
  
  const summaryData = createMockSummaryData(inputSector);
  render(<DCFModelsCard ticker="TEST.NS" summaryData={summaryData} />);
  
  // Check if the expected sector selection message was logged
  const sectorSelectionLogs = consoleSpy.mock.calls.filter(call => 
    call[0]?.includes?.('Auto-selecting model') || call[0]?.includes?.('Selected')
  );
  
  const foundExpectedSector = sectorSelectionLogs.some(call => 
    call.some(arg => typeof arg === 'string' && arg.includes(expectedNormalizedSector))
  );
  
  consoleSpy.mockRestore();
  return foundExpectedSector;
};

describe('Sector Normalization Utility Tests', () => {
  
  describe('Banking/Financial Services Normalization', () => {
    const bankingSectorVariations = [
      'BFSI',
      'Financial Services', 
      'BANKING',
      'banking',
      'Banks',
      'FINANCE',
      'finance'
    ];

    test.each(bankingSectorVariations)('normalizes "%s" to BFSI', (sector) => {
      expect(testSectorNormalization(sector, 'BFSI')).toBeTruthy();
    });
  });

  describe('IT/Technology Normalization', () => {
    const itSectorVariations = [
      'IT',
      'Information Technology',
      'INFORMATION TECHNOLOGY',
      'Software',
      'SOFTWARE',
      'Technology',
      'TECHNOLOGY',
      'Tech',
      'TECH'
    ];

    test.each(itSectorVariations)('normalizes "%s" to IT', (sector) => {
      expect(testSectorNormalization(sector, 'IT')).toBeTruthy();
    });
  });

  describe('Pharma/Healthcare Normalization', () => {
    const pharmaSectorVariations = [
      'PHARMA',
      'Pharmaceuticals',
      'PHARMACEUTICALS',
      'Healthcare',
      'HEALTHCARE',
      'Pharma & Healthcare',
      'PHARMA & HEALTHCARE',
      'Drugs',
      'DRUGS'
    ];

    test.each(pharmaSectorVariations)('normalizes "%s" to PHARMA', (sector) => {
      expect(testSectorNormalization(sector, 'PHARMA')).toBeTruthy();
    });
  });

  describe('Real Estate Normalization', () => {
    const realEstateSectorVariations = [
      'REAL ESTATE',
      'Real Estate',
      'REALTY',
      'Realty',
      'Property',
      'PROPERTY',
      'REAL_ESTATE'
    ];

    test.each(realEstateSectorVariations)('normalizes "%s" to REAL ESTATE', (sector) => {
      expect(testSectorNormalization(sector, 'REAL ESTATE')).toBeTruthy();
    });
  });

  describe('FMCG/Consumer Goods Normalization', () => {
    const fmcgSectorVariations = [
      'FMCG',
      'Consumer Goods',
      'CONSUMER GOODS',
      'Fast Moving Consumer Goods',
      'FAST MOVING CONSUMER GOODS',
      'Consumer',
      'CONSUMER',
      'CONSUMER_GOODS'
    ];

    test.each(fmcgSectorVariations)('normalizes "%s" to FMCG', (sector) => {
      expect(testSectorNormalization(sector, 'FMCG')).toBeTruthy();
    });
  });

  describe('Energy/Utilities Normalization', () => {
    const energySectorVariations = [
      'ENERGY',
      'Oil & Gas',
      'OIL & GAS',
      'Petroleum',
      'PETROLEUM', 
      'Power',
      'POWER',
      'Utilities',
      'UTILITIES'
    ];

    test.each(energySectorVariations)('normalizes "%s" to ENERGY', (sector) => {
      expect(testSectorNormalization(sector, 'ENERGY')).toBeTruthy();
    });
  });

  describe('Known Sectors Pass-Through', () => {
    const knownSectors = [
      'TELECOM',
      'AUTO', 
      'METALS',
      'CHEMICALS',
      'TEXTILES',
      'CEMENT',
      'DIVERSIFIED'
    ];

    test.each(knownSectors)('passes through known sector "%s" unchanged', (sector) => {
      expect(testSectorNormalization(sector, sector)).toBeTruthy();
    });
  });

  describe('Unknown Sectors → OTHER Category', () => {
    const unknownSectors = [
      'Mining',
      'MINING',
      'Agriculture',
      'AGRICULTURE',
      'Aviation',
      'AVIATION',
      'Logistics',
      'LOGISTICS',
      'Entertainment',
      'ENTERTAINMENT',
      'Education',
      'Media',
      'Defense',
      'Unknown Industry',
      'New Sector',
      'Random Name',
      '', // Empty string
      '   ', // Whitespace only
      'Non-existent Sector'
    ];

    test.each(unknownSectors)('normalizes unknown sector "%s" to OTHER', (sector) => {
      expect(testSectorNormalization(sector, 'OTHER')).toBeTruthy();
    });
  });

  describe('Case Insensitive Normalization', () => {
    const caseVariations = [
      { input: 'bfsi', expected: 'BFSI' },
      { input: 'Bfsi', expected: 'BFSI' },
      { input: 'information technology', expected: 'IT' },
      { input: 'Information Technology', expected: 'IT' },
      { input: 'INFORMATION TECHNOLOGY', expected: 'IT' },
      { input: 'pharmaceuticals', expected: 'PHARMA' },
      { input: 'Pharmaceuticals', expected: 'PHARMA' },
      { input: 'PHARMACEUTICALS', expected: 'PHARMA' },
      { input: 'real estate', expected: 'REAL ESTATE' },
      { input: 'Real Estate', expected: 'REAL ESTATE' },
      { input: 'REAL ESTATE', expected: 'REAL ESTATE' }
    ];

    test.each(caseVariations)('handles case variations: "$input" → "$expected"', ({ input, expected }) => {
      expect(testSectorNormalization(input, expected)).toBeTruthy();
    });
  });

  describe('Whitespace Handling', () => {
    const whitespaceVariations = [
      '  BFSI  ',
      '\tIT\t',
      ' Financial Services ',
      '  Information Technology  ',
      '\n PHARMA \n',
      ' Real Estate ',
      '  Consumer Goods  '
    ];

    test.each(whitespaceVariations)('handles whitespace in sector "%s"', (sector) => {
      // Should not crash and should normalize to appropriate category
      const summaryData = createMockSummaryData(sector);
      expect(() => {
        render(<DCFModelsCard ticker="TEST.NS" summaryData={summaryData} />);
      }).not.toThrow();
    });
  });

  describe('Edge Cases', () => {
    test('handles null/undefined sector gracefully', () => {
      // Test with null sector (TypeScript won't allow this directly, but JS runtime might)
      const summaryDataWithNullSector = {
        ...createMockSummaryData(''),
        sector: null as any
      };

      expect(() => {
        render(<DCFModelsCard ticker="TEST.NS" summaryData={summaryDataWithNullSector} />);
      }).not.toThrow();
    });

    test('handles special characters in sector name', () => {
      const specialCharacterSectors = [
        'IT & Software',
        'Oil & Gas',
        'Pharma & Healthcare',
        'Real-Estate',
        'Consumer_Goods',
        'IT/Software',
        'Banking/Finance'
      ];

      specialCharacterSectors.forEach(sector => {
        const summaryData = createMockSummaryData(sector);
        expect(() => {
          render(<DCFModelsCard ticker="TEST.NS" summaryData={summaryData} />);
        }).not.toThrow();
      });
    });

    test('handles very long sector names', () => {
      const longSectorName = 'Very Long Unknown Sector Name That Definitely Does Not Exist In Our System';
      expect(testSectorNormalization(longSectorName, 'OTHER')).toBeTruthy();
    });

    test('handles numeric strings as sector names', () => {
      const numericSectors = ['123', '0', '-1', '99999'];
      
      numericSectors.forEach(sector => {
        expect(testSectorNormalization(sector, 'OTHER')).toBeTruthy();
      });
    });
  });

  describe('Multiple Word Sector Names', () => {
    const multiWordSectors = [
      { input: 'Fast Moving Consumer Goods', expected: 'FMCG' },
      { input: 'Information Technology', expected: 'IT' },
      { input: 'Real Estate', expected: 'REAL ESTATE' },
      { input: 'Oil & Gas', expected: 'ENERGY' },
      { input: 'Pharma & Healthcare', expected: 'PHARMA' }
    ];

    test.each(multiWordSectors)('correctly handles multi-word sector: "$input" → "$expected"', ({ input, expected }) => {
      expect(testSectorNormalization(input, expected)).toBeTruthy();
    });
  });
});