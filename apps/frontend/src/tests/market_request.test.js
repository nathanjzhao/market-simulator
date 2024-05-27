const puppeteer = require('puppeteer');

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

describe('Login Test', () => {
  let browser1;
  let browser2;
  let page1;
  let page2;

  beforeAll(async () => {
    // browser1 = await puppeteer.launch();
    browser1 = await puppeteer.launch({headless: false});
    browser2 = await puppeteer.launch();
    page1 = await browser1.newPage();
    page2 = await browser2.newPage();
  });

  afterAll(async () => {
    await browser1.close();
    await browser2.close();
  });

  test('should login successfully on both pages', async () => {

    // Navigate to the home page in both tabs
    await Promise.all([
      page1.goto('http://localhost:3000'),
      page2.goto('http://localhost:3000')
    ]);
    

    // Click the "Go to Login" link in both tabs
    await Promise.all([
      page1.click('#login'),
      page2.click('#login')
    ]);
    
    // Wait for the input elements to be visible
    await Promise.all([
      page1.waitForSelector('#username', { visible: true }),
      page1.waitForSelector('#password', { visible: true }),
      page1.waitForSelector('#submit', { visible: true }),
      page2.waitForSelector('#username', { visible: true }),
      page2.waitForSelector('#password', { visible: true }),
      page2.waitForSelector('#submit', { visible: true }),
    ]);
        
    // Then type into them
    await page1.type('#username', 'test3');
    await page1.type('#password', 'test3');
    await page2.type('#username', 'test4');
    await page2.type('#password', 'test4');

    await page1.click('#submit');
    await page1.waitForNavigation();

    await page2.click('#submit');
    await page2.waitForNavigation();

    expect(page1.url()).toBe('http://localhost:3000/main_page');
    expect(page2.url()).toBe('http://localhost:3000/main_page');

    await page1.click('#start-fetching-kafka');

    // buy AAPL from page1
    await page1.click('#set-symbol-appl');
    await page1.type('#price', '100.00');
    await page1.type('#shares', '30');
    await page1.click('#make-request');
    
    await wait(3000)
    await page1.screenshot({ path: 'src/tests/screenshots/screenshot1.png' })

    // go to orderbook
    await page1.goto('http://localhost:3000/orderbook');
    await page1.click('#start-fetching-orderbook')

    // sell APPL from page2
    await page2.click('#set-symbol-appl');
    await page2.click('#toggle-direction')
    await page2.type('#price', '100.00');
    await page2.type('#shares', '20');
    await page2.click('#make-request');

    await wait(3000)
    await page1.screenshot({ path: 'src/tests/screenshots/screenshot2.png' })


  }, 20000);
});