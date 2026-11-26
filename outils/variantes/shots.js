const { chromium } = require('playwright');
const D = process.argv[2];
const variantes = [['a-actuelle',13],['b-reperes',13],['c-reperes-relief',13],['d-rues-gris',15],['e-carte-grise',15]];
(async () => {
  const b = await chromium.launch();
  for (const [v, zmax] of variantes) {
    const p = await b.newPage({viewport:{width:1000,height:640}, deviceScaleFactor:1}); const errs=[]; p.on('pageerror', e=>errs.push(e.message));
    await p.route('**/*', r => { const u = r.request().url();
      if (u.startsWith('http://t/')) return r.fulfill({path: D + new URL(u).pathname, contentType:'text/html'});
      if (/cdnjs\.cloudflare\.com|docs\.google\.com|googleusercontent\.com|wmts\.geo\.admin\.ch/.test(u)) return r.continue();
      return r.abort(); });
    await p.goto(`http://t/${v}.html`);
    await p.waitForFunction(() => !/Chargement/.test(document.getElementById('count').textContent), null, {timeout:20000});
    await p.waitForTimeout(2500); await p.screenshot({path:`${D}/${v}-1-vue.png`, clip:{x:0,y:0,width:660,height:640}});
    await p.evaluate(() => window.__map.setView([46.80, 7.15], 12, {animate:false})); await p.waitForTimeout(2500);
    await p.screenshot({path:`${D}/${v}-2-z12.png`, clip:{x:0,y:0,width:660,height:640}});
    await p.evaluate(z => window.__map.setView([46.8045, 7.170], z, {animate:false}), zmax); await p.waitForTimeout(2500);
    await p.screenshot({path:`${D}/${v}-3-proche.png`, clip:{x:0,y:0,width:660,height:640}});
    console.log(v, 'erreurs', errs); await p.close();
  }
  await b.close();
})();
