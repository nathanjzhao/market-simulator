const puppeteer = require('puppeteer');

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

    // Make request
    // Click on the combobox
    await page1.click('[role="combobox"]');
    await page1.waitForSelector('#react-select-2-live-region');
    const options = await page1.$$('#react-select-2-listbox [id^="react-select-2-option"]');
    if (options.length !== 10) {
      throw new Error('Expected 10 options, but found ' + options.length);
    }

    const optionText = await page1.evaluate(el => el.textContent, options[3]);

    if (optionText !== 'Option 4') {
      throw new Error('Expected the text of the 4th option to be "Option 4", but it was "' + optionText + '"');
    }

    await page1.click('#symbols-selector');
    await page1.type('#symbols-selector', 'BUY');
    await page1.type('#price', '100.00');
    await page1.type('#shares', '30');
    await page1.click('#make-request');
    
    await page1.screenshot({ path: 'src/tests/screenshots/screenshot1.png' })

    // await page1.goto('http://localhost:3000/orderbook')
    // await page1.waitForNavigation();

    // await page1.click('#start-fetching-orderbook');

    // await new Promise(resolve => setTimeout(resolve, 3000));


  }, 10000);
});