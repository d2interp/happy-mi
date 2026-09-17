import { test, expect } from '@playwright/test'
import { readdirSync } from 'node:fs'
import path from 'node:path'

function pages(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry =>
    entry.name.startsWith('.') || entry.name === 'public' ? [] : entry.isDirectory()
      ? pages(path.join(dir, entry.name))
      : entry.name.endsWith('.md') ? [path.join(dir, entry.name)] : [])
}

test('首页消融实验与重置', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('./')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('模型答对了')
  await page.getByLabel('将 h₂ 置零').check()
  await expect(page.locator('.lab-result')).toContainText('输出分数：1')
  await page.getByLabel('将 h₁ 置零').check()
  await expect(page.locator('.lab-result')).toContainText('输出分数：-1')
  await page.getByRole('button', { name: '重置', exact: true }).click()
  await expect(page.getByLabel('将 h₁ 置零')).not.toBeChecked()
  await page.getByLabel('输入 x', { exact: true }).selectOption('0')
  await expect(page.locator('.lab-result')).toContainText('输出分数：-1')
  expect(errors).toEqual([])
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true)
  await page.screenshot({ path: `artifacts/home-${test.info().project.name}.png`, fullPage: true })
})

test('正文公式、页面导航与移动端目录', async ({ page }, testInfo) => {
  await page.goto('chapters/04-transformer.html')
  await expect(page.locator('.vp-doc h1')).toContainText('Transformer')
  await expect(page.locator('mjx-container').first()).toBeVisible()
  await expect(page.locator('mjx-merror')).toHaveCount(0)
  if (testInfo.project.name === 'mobile') {
    await page.getByRole('button', { name: '课程目录' }).click()
    await expect(page.locator('.VPSidebar')).toBeVisible()
  } else {
    await expect(page.locator('.VPSidebar')).toBeVisible()
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true)
  await page.screenshot({ path: `artifacts/chapter-${testInfo.project.name}.png`, fullPage: true })
})

test('中文搜索可以找到因果修补章节', async ({ page }) => {
  await page.goto('./')
  await page.getByRole('button', { name: '搜索教程' }).click()
  const input = page.locator('#localsearch-input')
  await input.fill('激活修补')
  await expect(page.locator('.VPLocalSearchBox .result').first()).toBeVisible()
  await expect(page.locator('.VPLocalSearchBox')).toContainText('修补')
})

test('全书页面、公式和图片完整', async ({ page }) => {
  test.setTimeout(90000)
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  for (const file of pages('docs')) {
    const route = file.slice(5).replace(/index\.md$/, '').replace(/\.md$/, '.html')
    const response = await page.goto(route || './')
    expect(response?.status(), route).toBe(200)
    await expect(page.locator('h1').first()).toBeVisible()
    await expect(page.locator('mjx-merror, [data-mjx-error]')).toHaveCount(0)
    const broken = await page.locator('.vp-doc img').evaluateAll(images => images.filter(image =>
      !(image as HTMLImageElement).complete || (image as HTMLImageElement).naturalWidth === 0).map(image => (image as HTMLImageElement).src))
    expect(broken, route).toEqual([])
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), route).toBe(true)
  }
  expect(errors).toEqual([])
})

test('深色模式保持阅读与交互', async ({ page }) => {
  await page.goto('./')
  await page.evaluate(() => { localStorage.setItem('vitepress-theme-appearance', 'dark') })
  await page.reload()
  await expect(page.locator('html')).toHaveClass(/dark/)
  await page.getByLabel('将 h₁ 置零').check()
  await expect(page.locator('.lab-result')).toContainText('输出分数：-1')
  await page.screenshot({ path: `artifacts/dark-${test.info().project.name}.png`, fullPage: true })
})
