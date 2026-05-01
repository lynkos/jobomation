import { chromium, firefox, webkit } from "playwright";

interface BrowserData {
    browser: string;
    title: string;
    url: string;
}

const BROWSER_URL = "https://news.ycombinator.com";
const CSS_SELECTOR = ".hnname";

const BROWSER_OPTIONS = {
    viewport: { width: 1440, height: 900 },
    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    geolocation: { latitude: 25.753899, longitude: -80.377045, accuracy: 95 }, // GL Library @ FIU
};

const BROWSERS = [
    { name: 'Chromium', instance: await chromium.launch() },
    { name: 'Firefox', instance: await firefox.launch() },
    { name: 'WebKit', instance: await webkit.launch() }
];

async function scrapeBrowserTestPage(url = BROWSER_URL): Promise<BrowserData[]> {
    const results: BrowserData[] = [];

    for (const { name, instance } of BROWSERS) {
        const page = await instance.newPage(); // instance.newContext(BROWSER_OPTIONS);

        try {
            await page.goto(url);
            const title = await page.title();
            const page_url = page.url();

            results.push({ browser: name, title, url: page_url });

            // const new_page = await page.newPage();
            // await new_page.goto(url);
            
            // // Scrape data
            // const titles = await new_page.locator(CSS_SELECTOR).allTextContents();
            // console.log('Scraped Titles:', titles);
        } finally {
            await instance.close();
        }
    }

    return results;
}

scrapeBrowserTestPage().then(results => {
    console.log('Scraping results:');
    results.forEach(result => {
        console.log(`${result.browser}: ${result.title} (${result.url})`);
    });
}).catch(console.error);

// async function connectToBrowser() {
//     const browser = await firefox.launch({ headless: true });
//     const context = await browser.newContext(BROWSER_OPTIONS);

//     try {
//         const page = await context.newPage();

//         // Navigate to the target URL
//         await page.goto(BROWSER_URL);

//         // Scrape data
//         const titles = await page.locator(CSS_SELECTOR).allTextContents();
//         console.log('Scraped Titles:', titles);
//     } catch (err) {
//         return { success: false, error: String(err) };
//     } finally {
//         await context.close();
//         await browser.close();
//     }
// }

// connectToBrowser();