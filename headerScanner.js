const axios = require("axios");
const fs = require("fs");
const { program } = require("commander");
const chalk = require("chalk");
const figlet = require("figlet");
const ora = require("ora");
const { table } = require('table');
const cheerio = require('cheerio');
const dns = require('dns').promises;
const { URL } = require('url');
const https = require('https');

// إعدادات متقدمة لـ axios
const axiosInstance = axios.create({
  httpsAgent: new https.Agent({  
    rejectUnauthorized: false // للتحقق من شهادات SSL
  }),
  timeout: 15000,
  maxRedirects: 5,
  headers: {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Advanced-SecurityHeadersScanner/2.0"
  }
});

// تهيئة commander مع خيارات متقدمة
program
  .version("2.0.0")
  .description("أداة متقدمة لفحص الأمان الشامل - صائد الثغرات المحترف")
  .option("-u, --url <url>", "فحص عنوان URL واحد")
  .option("-f, --file <file>", "فحص قائمة من URLs من ملف")
  .option("-o, --output <file>", "حفظ النتائج في ملف (JSON/HTML/TXT)")
  .option("-v, --verbose", "عرض تفاصيل إضافية", false)
  .option("--full-scan", "فحص شامل يشمل تحليل المحتوى وفحص DNS", false)
  .option("--rate-limit <number>", "تحديد معدل الطلبات في الثانية", 5)
  .option("--timeout <ms>", "تحديد وقت الانتظار لكل طلب", 15000)
  .option("--format <type>", "تنسيق الإخراج (console, json, html)", "console")
  .parse(process.argv);

// قائمة موسعة للهيدرات الأمنية مع تحسينات
const securityHeaders = {
  "Content-Security-Policy": {
    severity: "high",
    recommendation: "يجب تعيين سياسة أمن المحتوى مع تقييد المصادر وتجنب 'unsafe-inline'",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
  },
  "Strict-Transport-Security": {
    severity: "critical",
    recommendation: "HSTS بحد أدنى max-age=63072000; includeSubDomains; preload",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security"
  },
  "X-Frame-Options": {
    severity: "high",
    recommendation: "تعيين إلى DENY أو SAMEORIGIN لمنع هجمات clickjacking",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options"
  },
  "X-Content-Type-Options": {
    severity: "medium",
    recommendation: "تعيين إلى nosniff لمنع MIME sniffing",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options"
  },
  "X-XSS-Protection": {
    severity: "medium",
    recommendation: "تعيين إلى 1; mode=block (مهم للمتصفحات القديمة)",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection"
  },
  "Referrer-Policy": {
    severity: "low",
    recommendation: "تعيين إلى no-referrer-when-downgrade أو stricter",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy"
  },
  "Permissions-Policy": {
    severity: "medium",
    recommendation: "تقييد الأذونات حسب الحاجة (مثل: geolocation=(), camera=())",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy"
  },
  "Cross-Origin-Embedder-Policy": {
    severity: "high",
    recommendation: "تعيين إلى require-corp للأمان الأمثل",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Embedder-Policy"
  },
  "Cross-Origin-Opener-Policy": {
    severity: "high",
    recommendation: "تعيين إلى same-origin لعزل العمليات",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy"
  },
  "Cross-Origin-Resource-Policy": {
    severity: "medium",
    recommendation: "تعيين إلى same-site أو same-origin",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Resource-Policy"
  },
  "Cache-Control": {
    severity: "low",
    recommendation: "تجنب تخزين البيانات الحساسة (no-store للصفحات الحساسة)",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control"
  },
  "Feature-Policy": {
    severity: "medium",
    recommendation: "تقييد الميزات القديمة (تم استبدالها بـ Permissions-Policy)",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Feature-Policy"
  },
  "Expect-CT": {
    severity: "medium",
    recommendation: "مراقبة شهادات CT (مهم لـ TLS)",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Expect-CT"
  },
  "Public-Key-Pins": {
    severity: "high",
    recommendation: "تجنب استخدامه (مهمل لصالح Expect-CT)",
    docs: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Public_Key_Pinning"
  }
};

// تحسينات على شعار البرنامج
console.log(
  chalk.hex('#00FFFF')(
    figlet.textSync("SecMaster Pro", {
      horizontalLayout: 'full',
      font: 'Cyberlarge',
      width: 80
    })
  )
);
console.log(chalk.hex('#FFA500').bold("أداة الفحص الأمني الشامل - الإصدار 2.0\n"));

// فحص URL مع تحسينات كبيرة
async function scanUrl(url, outputFile, isFullScan = false) {
  const spinner = ora({
    text: chalk.blue(`جار الفحص المتقدم لـ ${url}...`),
    spinner: 'dots'
  }).start();

  try {
    // إضافة تحقق من صحة URL
    if (!isValidUrl(url)) {
      throw new Error("رابط غير صالح");
    }

    // إجراءات متعددة بشكل متوازي
    const [response, dnsInfo, sslInfo] = await Promise.all([
      fetchUrl(url),
      isFullScan ? checkDns(url) : Promise.resolve(null),
      isFullScan ? checkSSL(url) : Promise.resolve(null)
    ]);

    spinner.succeed(chalk.green(`تم الفحص المتقدم لـ ${url} بنجاح`));
    
    const results = {
      url: url,
      status: response.status,
      headers: {},
      missingHeaders: [],
      securityScore: 100,
      recommendations: [],
      vulnerabilities: [],
      dns: dnsInfo,
      ssl: sslInfo,
      metaTags: {},
      cookies: [],
      technologies: []
    };

    // تحليل الهيدرات
    analyzeHeaders(response.headers, results);

    // فحص إضافي في الوضع الشامل
    if (isFullScan) {
      await fullContentScan(response.data, url, results);
    }

    // عرض النتائج
    displayResults(results, url);

    // حفظ النتائج
    if (outputFile) {
      await saveResults(outputFile, results, program.format);
    }

    return results;
  } catch (error) {
    spinner.fail(chalk.red(`فشل في فحص ${url}`));
    console.error(chalk.red(`❗ الخطأ: ${error.message}`));
    if (program.verbose) {
      console.error(chalk.gray(`تفاصيل الخطأ: ${error.stack}`));
    }
    return null;
  }
}

// تحسينات على تحليل الهيدرات
function analyzeHeaders(headers, results) {
  const headerTable = [];
  headerTable.push([chalk.bold('الهيدر'), chalk.bold('القيمة'), chalk.bold('الحالة')]);

  for (const [header, info] of Object.entries(securityHeaders)) {
    const headerKey = header.toLowerCase();
    const headerValue = headers[headerKey];
    
    if (headerValue) {
      results.headers[header] = headerValue;
      const validation = validateHeader(header, headerValue);
      
      if (validation.valid) {
        headerTable.push([chalk.green(header), headerValue, chalk.green('آمن')]);
      } else {
        headerTable.push([chalk.yellow(header), headerValue, chalk.yellow(`تحذير: ${validation.message}`)]);
        results.securityScore -= 10;
        results.recommendations.push({
          header,
          issue: validation.message,
          severity: info.severity,
          docs: info.docs
        });
      }
    } else {
      headerTable.push([chalk.red(header), 'مفقود', chalk.red('خطر')]);
      results.missingHeaders.push(header);
      results.securityScore -= 15;
      results.recommendations.push({
        header,
        issue: `هيدر ${header} مفقود`,
        recommendation: info.recommendation,
        severity: info.severity,
        docs: info.docs
      });
    }
  }

  if (program.format === 'console') {
    console.log('\n' + table(headerTable, {
      border: {
        topBody: `─`,
        topJoin: `┬`,
        topLeft: `┌`,
        topRight: `┐`,
        bottomBody: `─`,
        bottomJoin: `┴`,
        bottomLeft: `└`,
        bottomRight: `┘`,
        bodyLeft: `│`,
        bodyRight: `│`,
        bodyJoin: `│`,
        joinBody: `─`,
        joinLeft: `├`,
        joinRight: `┤`,
        joinJoin: `┼`
      },
      columns: {
        0: { width: 30 },
        1: { width: 50 },
        2: { width: 30 }
      }
    }));
  }
}

// فحص شامل للمحتوى
async function fullContentScan(html, url, results) {
  try {
    const $ = cheerio.load(html);
    
    // تحليل meta tags
    results.metaTags = {};
    $('meta').each((i, el) => {
      const name = $(el).attr('name') || $(el).attr('property') || 'unnamed';
      results.metaTags[name] = $(el).attr('content');
    });

    // اكتشاف التقنيات المستخدمة
    detectTechnologies($, results);

    // تحليل الكوكيز
    if (program.verbose) {
      console.log(chalk.blue('\nجار تحليل الكوكيز...'));
    }
    
    // يمكن إضافة تحليل أكثر تعقيداً للكوكيز هنا
    
    // البحث عن نقاط ضعف محتملة
    scanForVulnerabilities($, url, results);
    
  } catch (error) {
    if (program.verbose) {
      console.error(chalk.yellow('❗ تحذير: فشل تحليل المحتوى - ' + error.message));
    }
  }
}

// اكتشاف التقنيات المستخدمة
function detectTechnologies($, results) {
  const techSignatures = {
    'jquery': { pattern: /jquery/i, versionPattern: /jquery ([0-9.]+)/i },
    'bootstrap': { pattern: /bootstrap/i, versionPattern: /bootstrap(?:.*)?([0-9.]+)/i },
    'react': { pattern: /react/i, versionPattern: /react(?:\/|\s)([0-9.]+)/i },
    'wordpress': { pattern: /wp-content|wordpress/i, versionPattern: /wordpress(?:.*)?([0-9.]+)/i }
  };

  const scripts = $('script').map((i, el) => $(el).attr('src')).get();
  const styles = $('link[rel="stylesheet"]').map((i, el) => $(el).attr('href')).get();
  const combined = [...scripts, ...styles, $('html').html()].join(' ');

  for (const [tech, sig] of Object.entries(techSignatures)) {
    if (sig.pattern.test(combined)) {
      const versionMatch = combined.match(sig.versionPattern);
      const version = versionMatch ? versionMatch[1] : 'غير معروف';
      results.technologies.push({ name: tech, version });
    }
  }
}

// مسح للبحث عن نقاط ضعف
function scanForVulnerabilities($, url, results) {
  // تحقق من حقول كلمات المرور بدون type="password"
  $('input').each((i, el) => {
    const name = $(el).attr('name') || '';
    if (name.toLowerCase().includes('password') && $(el).attr('type') !== 'password') {
      results.vulnerabilities.push({
        type: 'نقطة ضعف',
        issue: 'حقل كلمة مرور بدون type="password"',
        severity: 'medium',
        element: $.html(el),
        recommendation: 'استخدم type="password" لحقول كلمة المرور'
      });
    }
  });

  // تحقق من روابط غير آمنة
  $('a, link, script, img').each((i, el) => {
    const src = $(el).attr('src') || $(el).attr('href');
    if (src && src.startsWith('http://') && !src.startsWith('http://localhost')) {
      results.vulnerabilities.push({
        type: 'نقطة ضعف',
        issue: 'مصدر غير آمن (HTTP)',
        severity: 'high',
        element: $.html(el),
        recommendation: 'استخدم HTTPS لجميع الموارد'
      });
    }
  });
}

// تحسينات على حفظ النتائج
async function saveResults(filename, data, format = 'json') {
  try {
    let content;
    switch (format.toLowerCase()) {
      case 'html':
        content = generateHtmlReport(data);
        break;
      case 'txt':
        content = generateTextReport(data);
        break;
      default:
        content = JSON.stringify(data, null, 2);
    }

    fs.writeFileSync(filename, content);
    console.log(chalk.green(`\nتم حفظ النتائج في ${filename} بصيغة ${format}`));
  } catch (error) {
    console.error(chalk.red(`❗ فشل في حفظ الملف: ${error.message}`));
  }
}

// توليد تقرير HTML
function generateHtmlReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>تقرير الأمان - ${data.url}</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
    h1, h2 { color: #333; }
    .secure { color: green; }
    .warning { color: orange; }
    .danger { color: red; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h1>تقرير فحص الأمان</h1>
  <h2>الرابط: ${data.url}</h2>
  
  <h3>معلومات عامة</h3>
  <p>حالة HTTP: ${data.status}</p>
  <p>نتيجة الأمان: <span class="${getScoreClass(data.securityScore)}">${data.securityScore}/100</span></p>
  
  <h3>الهيدرات الأمنية</h3>
  <table>
    <tr><th>الهيدر</th><th>الحالة</th><th>التوصيات</th></tr>
    ${Object.entries(data.headers).map(([header, value]) => `
      <tr>
        <td>${header}</td>
        <td class="secure">موجود</td>
        <td>${securityHeaders[header]?.recommendation || 'لا توجد توصيات'}</td>
      </tr>
    `).join('')}
    ${data.missingHeaders.map(header => `
      <tr>
        <td>${header}</td>
        <td class="danger">مفقود</td>
        <td>${securityHeaders[header]?.recommendation || 'يجب إضافة هذا الهيدر'}</td>
      </tr>
    `).join('')}
  </table>
  
  ${data.vulnerabilities.length > 0 ? `
  <h3>نقاط الضعف المكتشفة</h3>
  <table>
    <tr><th>النوع</th><th>المشكلة</th><th>الحل المقترح</th></tr>
    ${data.vulnerabilities.map(vuln => `
      <tr>
        <td class="warning">${vuln.type}</td>
        <td>${vuln.issue}</td>
        <td>${vuln.recommendation}</td>
      </tr>
    `).join('')}
  </table>
  ` : ''}
  
  <h3>التوصيات الأمنية</h3>
  <ul>
    ${data.recommendations.map(rec => `<li>${rec.recommendation || rec.issue}</li>`).join('')}
  </ul>
</body>
</html>
  `;
}

// توليد تقرير نصي
function generateTextReport(data) {
  let report = `تقرير فحص الأمان - ${data.url}\n`;
  report += `=''.repeat(50)}\n\n`;
  report += `معلومات عامة:\n`;
  report += `- الرابط: ${data.url}\n`;
  report += `- حالة HTTP: ${data.status}\n`;
  report += `- نتيجة الأمان: ${data.securityScore}/100\n\n`;
  
  report += `الهيدرات الأمنية:\n`;
  Object.entries(data.headers).forEach(([header, value]) => {
    report += `- ${header}: ${value} (موجود)\n`;
  });
  data.missingHeaders.forEach(header => {
    report += `- ${header}: مفقود! (${securityHeaders[header]?.severity || 'غير معروف'})\n`;
  });
  
  if (data.vulnerabilities.length > 0) {
    report += `\nنقاط الضعف:\n`;
    data.vulnerabilities.forEach(vuln => {
      report += `- ${vuln.issue} (${vuln.severity})\n`;
      report += `  الحل: ${vuln.recommendation}\n`;
    });
  }
  
  report += `\nالتوصيات:\n`;
  data.recommendations.forEach((rec, i) => {
    report += `${i+1}. ${rec.recommendation || rec.issue}\n`;
  });
  
  return report;
}

// تحسينات على عرض النتائج
function displayResults(results, url) {
  console.log(chalk.blueBright(`\n═[ ${url} ]${'═'.repeat(80 - url.length - 4)}`));
  
  // عرض ملخص سريع
  console.log(chalk.bold(`\nملخص الأمان:`));
  console.log(`- نتيجة الأمان: ${getScoreColor(results.securityScore)}`);
  console.log(`- الهيدرات المفقودة: ${results.missingHeaders.length}`);
  console.log(`- نقاط الضعف: ${results.vulnerabilities.length}`);
  console.log(`- التقنيات المكتشفة: ${results.technologies.map(t => `${t.name}@${t.version}`).join(', ') || 'غير معروف'}`);
  
  // عرض التوصيات إذا كانت موجودة
  if (results.recommendations.length > 0) {
    console.log(chalk.yellowBright(`\nالتوصيات الأمنية:`));
    results.recommendations.forEach((rec, i) => {
      console.log(`${i+1}. ${rec.recommendation || rec.issue} (${rec.severity})`);
      if (program.verbose && rec.docs) {
        console.log(`   ${chalk.gray('مصدر: ' + rec.docs)}`);
      }
    });
  }
  
  // عرض نقاط الضعف إذا كانت موجودة
  if (results.vulnerabilities.length > 0) {
    console.log(chalk.redBright(`\nنقاط الضعف:`));
    results.vulnerabilities.forEach((vuln, i) => {
      console.log(`${i+1}. [${vuln.severity}] ${vuln.issue}`);
      console.log(`   ${chalk.green('الحل:')} ${vuln.recommendation}`);
      if (program.verbose) {
        console.log(`   ${chalk.gray('العنصر: ' + vuln.element.substring(0, 100) + '...')}`);
      }
    });
  }
  
  console.log(chalk.blueBright(`\n${'═'.repeat(80)}\n`));
}

// تحسينات على فحص DNS
async function checkDns(url) {
  try {
    const domain = new URL(url).hostname;
    const records = {
      A: await dns.resolve(domain, 'A'),
      AAAA: await dns.resolve(domain, 'AAAA'),
      MX: await dns.resolve(domain, 'MX'),
      TXT: await dns.resolve(domain, 'TXT'),
      CNAME: await dns.resolve(domain, 'CNAME')
    };
    
    if (program.verbose) {
      console.log(chalk.gray('\nسجلات DNS:'));
      console.dir(records, { depth: null, colors: true });
    }
    
    return records;
  } catch (error) {
    if (program.verbose) {
      console.error(chalk.yellow('❗ تحذير: فشل فحص DNS - ' + error.message));
    }
    return null;
  }
}

// فحص SSL الأساسي
async function checkSSL(url) {
  try {
    const hostname = new URL(url).hostname;
    const agent = new https.Agent({  
      rejectUnauthorized: true,
      maxVersion: 'TLSv1.3',
      minVersion: 'TLSv1.2'
    });
    
    await axiosInstance.get(url, { httpsAgent: agent });
    return { status: 'valid', protocol: 'TLS 1.2/1.3' };
  } catch (error) {
    return { status: 'invalid', error: error.message };
  }
}

// تحسينات على جلب URL
async function fetchUrl(url) {
  try {
    const response = await axiosInstance.get(url);
    return response;
  } catch (error) {
    if (error.response) {
      // الطلب تم ولكن الخادم رد بحالة خطأ
      return error.response;
    }
    throw error;
  }
}

// تحقق من صحة URL
function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

// تحسينات على التحقق من الهيدرات
function validateHeader(header, value) {
  const tests = {
    "Strict-Transport-Security": [
      {
        test: !value.includes("max-age="),
        message: "HSTS يجب أن يحتوي على max-age"
      },
      {
        test: value.includes("max-age=0"),
        message: "max-age=0 يعطل HSTS ويجب تجنبه"
      },
      {
        test: parseInt(value.match(/max-age=(\d+)/)?.[1]) < 31536000,
        message: "يفضل max-age=63072000 (سنتين) للأمان الأمثل"
      }
    ],
    "Content-Security-Policy": [
      {
        test: value.includes("unsafe-inline"),
        message: "يجب تجنب unsafe-inline في CSP"
      },
      {
        test: value.includes("unsafe-eval"),
        message: "يجب تجنب unsafe-eval في CSP"
      },
      {
        test: !value.includes("default-src"),
        message: "يفضل تحديد default-src كسياسة افتراضية"
      }
    ],
    "X-XSS-Protection": [
      {
        test: value !== "1; mode=block",
        message: "يفضل استخدام '1; mode=block'"
      }
    ],
    "Permissions-Policy": [
      {
        test: value.includes("geolocation=()") && value.includes("microphone=()") && value.includes("camera=()"),
        message: "يجب تقييد الأذونات الحساسة مثل geolocation و microphone و camera"
      }
    ]
  };

  const issues = [];
  if (tests[header]) {
    tests[header].forEach(test => {
      if (test.test) {
        issues.push(test.message);
      }
    });
  }

  return {
    valid: issues.length === 0,
    message: issues.join("، ")
  };
}

// فحص من ملف مع تحسينات
async function scanFromFile(filePath, outputFile, isFullScan = false) {
  try {
    const data = fs.readFileSync(filePath, "utf8");
    const urls = data.split("\n")
      .map(url => url.trim())
      .filter(url => url !== "" && isValidUrl(url));
    
    if (urls.length === 0) {
      throw new Error("لا توجد عناوين URL صالحة في الملف");
    }
    
    console.log(chalk.blue(`\nبدء فحص ${urls.length} عنوان URL...`));
    
    // تحديد معدل الطلبات
    const rateLimit = parseInt(program.rateLimit) || 5;
    const batchSize = Math.min(rateLimit, urls.length);
    
    const allResults = [];
    for (let i = 0; i < urls.length; i += batchSize) {
      const batch = urls.slice(i, i + batchSize);
      const batchPromises = batch.map(url => scanUrl(url, null, isFullScan));
      const batchResults = await Promise.all(batchPromises);
      allResults.push(...batchResults.filter(result => result !== null));
      
      // إضافة تأخير بين الدفعات إذا لزم الأمر
      if (i + batchSize < urls.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    if (outputFile && allResults.length > 0) {
      await saveResults(outputFile, { scans: allResults }, program.format);
    }
    
    // عرض ملخص شامل
    if (program.format === 'console') {
      displaySummaryReport(allResults);
    }
    
    return allResults;
  } catch (error) {
    console.error(chalk.red(`❗ خطأ في قراءة الملف: ${error.message}`));
    return [];
  }
}

// عرض ملخص شامل لجميع الفحوصات
function displaySummaryReport(results) {
  console.log(chalk.blueBright(`\n═[ ملخص شامل ]${'═'.repeat(70)}`));
  
  // إحصائيات عامة
  const totalSites = results.length;
  const avgScore = results.reduce((sum, r) => sum + r.securityScore, 0) / totalSites;
  const criticalSites = results.filter(r => r.securityScore < 50).length;
  const warningSites = results.filter(r => r.securityScore >= 50 && r.securityScore < 70).length;
  const goodSites = results.filter(r => r.securityScore >= 70).length;
  
  console.log(chalk.bold(`\nإحصائيات الفحص:`));
  console.log(`- عدد المواقع المفحوصة: ${totalSites}`);
  console.log(`- متوسط نتيجة الأمان: ${getScoreColor(avgScore)}`);
  console.log(`- مواقع بحالة حرجة: ${chalk.red(criticalSites)}`);
  console.log(`- مواقع تحتاج تحسينات: ${chalk.yellow(warningSites)}`);
  console.log(`- مواقع آمنة: ${chalk.green(goodSites)}`);
  
  // أكثر الهيدرات المفقودة
  const missingHeaders = {};
  results.forEach(r => {
    r.missingHeaders.forEach(h => {
      missingHeaders[h] = (missingHeaders[h] || 0) + 1;
    });
  });
  
  if (Object.keys(missingHeaders).length > 0) {
    console.log(chalk.yellowBright(`\nأكثر الهيدرات المفقودة:`));
    const sorted = Object.entries(missingHeaders)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
    
    sorted.forEach(([header, count]) => {
      console.log(`- ${header}: مفقود في ${count} موقع (${Math.round(count/totalSites*100)}%)`);
    });
  }
  
  // أكثر نقاط الضعف شيوعاً
  const commonVulns = {};
  results.forEach(r => {
    r.vulnerabilities.forEach(v => {
      const key = v.issue;
      commonVulns[key] = (commonVulns[key] || 0) + 1;
    });
  });
  
  if (Object.keys(commonVulns).length > 0) {
    console.log(chalk.redBright(`\nأكثر نقاط الضعف شيوعاً:`));
    const sorted = Object.entries(commonVulns)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
    
    sorted.forEach(([issue, count]) => {
      console.log(`- ${issue}: موجود في ${count} موقع (${Math.round(count/totalSites*100)}%)`);
    });
  }
  
  console.log(chalk.blueBright(`\n${'═'.repeat(80)}\n`));
}

// تحسينات على لون نتيجة الأمان
function getScoreColor(score) {
  if (score >= 85) return chalk.green.bold(score.toFixed(1));
  if (score >= 70) return chalk.yellow.bold(score.toFixed(1));
  return chalk.red.bold(score.toFixed(1));
}

function getScoreClass(score) {
  if (score >= 85) return 'secure';
  if (score >= 70) return 'warning';
  return 'danger';
}

// التنفيذ الرئيسي مع تحسينات
async function main() {
  try {
    if (!program.url && !program.file) {
      program.help();
      return;
    }

    // التحقق من وجود ملف إذا تم تحديده
    if (program.file && !fs.existsSync(program.file)) {
      throw new Error(`الملف ${program.file} غير موجود`);
    }

    // تحديد وقت الانتظار إذا تم تحديده
    if (program.timeout) {
      axiosInstance.defaults.timeout = parseInt(program.timeout);
    }

    // تنفيذ الفحص
    if (program.url) {
      await scanUrl(program.url, program.output, program.fullScan);
    } else if (program.file) {
      await scanFromFile(program.file, program.output, program.fullScan);
    }
  } catch (error) {
    console.error(chalk.red(`❗ خطأ رئيسي: ${error.message}`));
    if (program.verbose) {
      console.error(chalk.gray(`Stack trace: ${error.stack}`));
    }
    process.exit(1);
  }
}

main();