const puppeteer = require('puppeteer');

(async () => {
    console.log('🚀 启动 Puppeteer...');
    
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-gpu', '--window-size=1920,1080'],
        executablePath: '/opt/chrome/chrome'
    });
    
    console.log('✅ 浏览器已启动');
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    await page.goto('https://agentcoin.site');
    console.log(`✅ 已加载页面: ${await page.title()}`);
    
    await page.screenshot({ path: '/tmp/puppeteer_test.png' });
    console.log('✅ 截图已保存: /tmp/puppeteer_test.png');
    
    const content = await page.content();
    console.log(`📄 页面内容长度: ${content.length} 字符`);
    
    await browser.close();
    console.log('✅ 浏览器已关闭');
})();
