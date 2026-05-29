#!/usr/bin/env node

/**
 * GET ACCURATE KUCOIN TRADING REQUIREMENTS
 * Fix the diagnostic script to handle API response format
 */

const https = require('https');
const crypto = require('crypto');
require('dotenv').config();

const apiKey = process.env.KUCOIN_API_KEY;
const secretKey = process.env.KUCOIN_SECRET_KEY;
const passphrase = process.env.KUCOIN_API_PASSPHRASE;

function sign(str) {
  return crypto.createHmac('sha256', secretKey).update(str).digest('base64');
}

async function makeRequest(method, endpoint, body = '') {
  return new Promise((resolve, reject) => {
    const timestamp = Date.now().toString();
    const what = timestamp + method + endpoint + body;
    const signature = sign(what);
    const passphraseSigned = sign(passphrase);
    
    const options = {
      hostname: 'api.kucoin.com',
      port: 443,
      path: endpoint,
      method: method,
      headers: {
        'KC-API-KEY': apiKey,
        'KC-API-SIGN': signature,
        'KC-API-TIMESTAMP': timestamp,
        'KC-API-PASSPHRASE': passphraseSigned,
        'KC-API-KEY-VERSION': '2',
        'Content-Type': 'application/json'
      }
    };
    
    if (body) {
      options.headers['Content-Length'] = Buffer.byteLength(body);
    }
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === '200000') {
            resolve(result.data);
          } else {
            reject(new Error(`API Error: ${result.msg} (Code: ${result.code})`));
          }
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });
    
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getTradingRequirements() {
  console.log('📏 Getting Accurate KuCoin Trading Requirements...');
  console.log('=' .repeat(60));
  
  try {
    const tradingPairs = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'USDT-USDC'];
    
    for (const pair of tradingPairs) {
      console.log(`\n${pair}:`);
      
      // Get symbol info
      try {
        const symbolInfo = await makeRequest('GET', `/api/v1/symbols/${pair}`);
        
        console.log(`   Minimum Funds: $${symbolInfo.quoteMinFunds}`);
        console.log(`   Size Increment: ${symbolInfo.baseIncrement}`);
        console.log(`   Price Increment: ${symbolInfo.quoteIncrement}`);
        
        // Get current price
        const ticker = await makeRequest('GET', `/api/v1/market/orderbook/level1?symbol=${pair}`);
        const price = parseFloat(ticker.price);
        
        console.log(`   Current Price: $${price.toFixed(pair === 'USDT-USDC' ? 4 : 2)}`);
        
        // Calculate minimum valid order
        const minFunds = parseFloat(symbolInfo.quoteMinFunds);
        const sizeIncrement = parseFloat(symbolInfo.baseIncrement);
        const priceIncrement = parseFloat(symbolInfo.quoteIncrement);
        
        // Calculate minimum size to meet funds requirement
        const minSizeRequired = Math.ceil(minFunds / price / sizeIncrement) * sizeIncrement;
        const minOrderValue = minSizeRequired * price;
        
        console.log(`   Minimum Size: ${minSizeRequired.toFixed(8)} base units`);
        console.log(`   Minimum Value: $${minOrderValue.toFixed(2)}`);
        
        // Round price to valid increment
        const roundedPrice = Math.floor(price / priceIncrement) * priceIncrement;
        console.log(`   Rounded Price: $${roundedPrice.toFixed(pair === 'USDT-USDC' ? 4 : 2)}`);
        
      } catch (error) {
        console.log(`   ❌ Error: ${error.message}`);
      }
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log('✅ Trading requirements obtained');
    
  } catch (error) {
    console.error('\n❌ Failed to get trading requirements:', error.message);
  }
}

getTradingRequirements();