// Popular Indian stock symbols mapping
export interface StockSymbol {
  ticker: string;
  name: string;
  sector: string;
  aliases: string[];
  marketCap?: string;  // Added for UI enhancement
  description?: string; // Added for UI enhancement
}

export const POPULAR_STOCKS: StockSymbol[] = [
  // Banking
  { ticker: "SBIN.NS", name: "State Bank of India", sector: "Banking", aliases: ["SBI", "SBIN", "STATE BANK"] },
  { ticker: "HDFCBANK.NS", name: "HDFC Bank Limited", sector: "Banking", aliases: ["HDFC", "HDFC BANK", "HDFCBANK"] },
  { ticker: "ICICIBANK.NS", name: "ICICI Bank Limited", sector: "Banking", aliases: ["ICICI", "ICICI BANK", "ICICIBANK"] },
  { ticker: "AXISBANK.NS", name: "Axis Bank Limited", sector: "Banking", aliases: ["AXIS", "AXIS BANK", "AXISBANK"] },
  { ticker: "KOTAKBANK.NS", name: "Kotak Mahindra Bank", sector: "Banking", aliases: ["KOTAK", "KOTAK BANK", "KOTAKBANK"] },
  
  // IT Services
  { ticker: "TCS.NS", name: "Tata Consultancy Services", sector: "IT Services", aliases: ["TCS", "TATA CONSULTANCY"] },
  { ticker: "INFY.NS", name: "Infosys Limited", sector: "IT Services", aliases: ["INFY", "INFOSYS"] },
  { ticker: "WIPRO.NS", name: "Wipro Limited", sector: "IT Services", aliases: ["WIPRO"] },
  { ticker: "TECHM.NS", name: "Tech Mahindra Limited", sector: "IT Services", aliases: ["TECH MAHINDRA", "TECHM"] },
  { ticker: "LTI.NS", name: "LTI Mindtree Limited", sector: "IT Services", aliases: ["LTI", "MINDTREE", "LTI MINDTREE"] },
  
  // Oil & Gas
  { ticker: "RELIANCE.NS", name: "Reliance Industries", sector: "Oil & Gas", aliases: ["RELIANCE", "RIL"] },
  { ticker: "ONGC.NS", name: "Oil & Natural Gas Corporation", sector: "Oil & Gas", aliases: ["ONGC"] },
  { ticker: "IOC.NS", name: "Indian Oil Corporation", sector: "Oil & Gas", aliases: ["IOC", "INDIAN OIL"] },
  
  // FMCG
  { ticker: "HINDUNILVR.NS", name: "Hindustan Unilever", sector: "FMCG", aliases: ["HUL", "HINDUSTAN UNILEVER", "HINDUNILVR"] },
  { ticker: "ITC.NS", name: "ITC Limited", sector: "FMCG", aliases: ["ITC"] },
  { ticker: "NESTLEIND.NS", name: "Nestle India", sector: "FMCG", aliases: ["NESTLE", "NESTLEIND"] },
  { ticker: "BRITANNIA.NS", name: "Britannia Industries", sector: "FMCG", aliases: ["BRITANNIA"] },
  
  // Pharma
  { ticker: "SUNPHARMA.NS", name: "Sun Pharmaceutical", sector: "Pharma", aliases: ["SUN PHARMA", "SUNPHARMA"] },
  { ticker: "DRREDDY.NS", name: "Dr. Reddy's Laboratories", sector: "Pharma", aliases: ["DR REDDY", "DRREDDY", "DRL"] },
  { ticker: "CIPLA.NS", name: "Cipla Limited", sector: "Pharma", aliases: ["CIPLA"] },
  { ticker: "APOLLOHOSP.NS", name: "Apollo Hospitals", sector: "Healthcare", aliases: ["APOLLO", "APOLLOHOSP"] },
  
  // Auto
  { ticker: "MARUTI.NS", name: "Maruti Suzuki India", sector: "Auto", aliases: ["MARUTI", "MARUTI SUZUKI"] },
  { ticker: "TATAMOTORS.NS", name: "Tata Motors Limited", sector: "Auto", aliases: ["TATA MOTORS", "TATAMOTORS"] },
  { ticker: "M&M.NS", name: "Mahindra & Mahindra", sector: "Auto", aliases: ["MAHINDRA", "M&M", "MM"] },
  { ticker: "BAJAJ-AUTO.NS", name: "Bajaj Auto Limited", sector: "Auto", aliases: ["BAJAJ AUTO", "BAJAJ-AUTO"] },
  
  // Metals
  { ticker: "TATASTEEL.NS", name: "Tata Steel Limited", sector: "Metals", aliases: ["TATA STEEL", "TATASTEEL"] },
  { ticker: "HINDALCO.NS", name: "Hindalco Industries", sector: "Metals", aliases: ["HINDALCO"] },
  { ticker: "JSWSTEEL.NS", name: "JSW Steel Limited", sector: "Metals", aliases: ["JSW STEEL", "JSWSTEEL", "JSW"] },
  
  // Telecom
  { ticker: "BHARTIARTL.NS", name: "Bharti Airtel Limited", sector: "Telecom", aliases: ["AIRTEL", "BHARTI AIRTEL", "BHARTIARTL"] },
  { ticker: "IDEA.NS", name: "Vodafone Idea Limited", sector: "Telecom", aliases: ["IDEA", "VODAFONE IDEA", "VI"] },
  
  // Cement
  { ticker: "ULTRACEMCO.NS", name: "UltraTech Cement", sector: "Cement", aliases: ["ULTRATECH", "ULTRACEMCO"] },
  { ticker: "AMBUJACEM.NS", name: "Ambuja Cements", sector: "Cement", aliases: ["AMBUJA", "AMBUJACEM"] },
  
  // Power
  { ticker: "NTPC.NS", name: "NTPC Limited", sector: "Power", aliases: ["NTPC"] },
  { ticker: "POWERGRID.NS", name: "Power Grid Corporation", sector: "Power", aliases: ["POWER GRID", "POWERGRID"] },
];

// Function to search stocks by query
export function searchStocks(query: string, limit: number = 10): StockSymbol[] {
  if (!query || query.length < 1) return [];
  
  const searchTerm = query.toUpperCase().trim();
  const results: { stock: StockSymbol; score: number }[] = [];
  
  for (const stock of POPULAR_STOCKS) {
    let score = 0;
    
    // Exact ticker match (highest priority)
    if (stock.ticker.replace('.NS', '') === searchTerm) {
      score = 100;
    }
    // Ticker starts with query
    else if (stock.ticker.replace('.NS', '').startsWith(searchTerm)) {
      score = 90;
    }
    // Alias exact match
    else if (stock.aliases.some(alias => alias === searchTerm)) {
      score = 80;
    }
    // Alias starts with query
    else if (stock.aliases.some(alias => alias.startsWith(searchTerm))) {
      score = 70;
    }
    // Company name starts with query
    else if (stock.name.toUpperCase().startsWith(searchTerm)) {
      score = 60;
    }
    // Company name contains query
    else if (stock.name.toUpperCase().includes(searchTerm)) {
      score = 50;
    }
    // Alias contains query
    else if (stock.aliases.some(alias => alias.includes(searchTerm))) {
      score = 40;
    }
    
    if (score > 0) {
      results.push({ stock, score });
    }
  }
  
  // Sort by score (descending) and return top results
  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(result => result.stock);
}