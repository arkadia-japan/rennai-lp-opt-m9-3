Param(
  [string]$Template = "index.html",
  [string]$Markdown = "contents.md",
  [string]$OutDir = "dist"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Escape-Html([string]$s){
  if ($null -eq $s) { return '' }
  $s.Replace('&','&amp;').Replace('<','&lt;').Replace('>','&gt;').Replace('"','&quot;').Replace("'",'&#39;')
}

function Read-ShiftJis([string]$path){
  $bytes = [System.IO.File]::ReadAllBytes($path)
  $enc = [System.Text.Encoding]::GetEncoding(932) # Shift-JIS/CP932
  return $enc.GetString($bytes)
}

function Read-JsonSmart([string]$path){
  try { return Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json } catch {
    try { return (Read-ShiftJis -path $path) | ConvertFrom-Json } catch { return $null }
  }
}

if (-not (Test-Path $Template)) { throw "Template not found: $Template" }
if (-not (Test-Path $Markdown)) { throw "Markdown not found: $Markdown" }

$templateHtml = Get-Content -LiteralPath $Template -Raw -Encoding UTF8
$md = Read-ShiftJis -path $Markdown

$lines = ($md -split "\r?\n")

# Extract hero title and lead
# 1) Prefer explicit hero section heading (## ヒーロー | ## ファーストビュー | ## HERO)
# 2) Fallback to first non-CTA h2 and its following paragraph
$heroTitle = ''
$heroLead = ''
$skipLine = New-Object 'System.Collections.Generic.HashSet[int]'

for ($i = 0; $i -lt $lines.Count; $i++){
  $line = $lines[$i]
  if ($line -match '^##\s*CTA\d+'){ continue }
  if ($line -match '^##\s*(ヒーロー|ﾋｰﾛｰ|ファーストビュー|ﾌｧｰｽﾄﾋﾞｭｰ|HERO)\b'){ 
    # Use next non-empty non-heading as hero title, next as lead
    for ($j = $i+1; $j -lt $lines.Count; $j++){
      $nxt = $lines[$j]
      if ($nxt -match '^\s*$'){ continue }
      if ($nxt -match '^#'){ break }
      if ([string]::IsNullOrWhiteSpace($heroTitle)){
        $heroTitle = $nxt.Trim(); $skipLine.Add($j) | Out-Null; continue
      }
      if ([string]::IsNullOrWhiteSpace($heroLead)){
        $heroLead = $nxt.Trim(); $skipLine.Add($j) | Out-Null; break
      }
    }
    $skipLine.Add($i) | Out-Null
    break
  }
  if ($line -match '^##\s*(.+)$'){
    $heroTitle = $Matches[1].Trim()
    $skipLine.Add($i) | Out-Null
    # find first following non-empty non-heading line as lead
    for ($j = $i+1; $j -lt $lines.Count; $j++){
      $nxt = $lines[$j]
      if ($nxt -match '^\s*$'){ continue }
      if ($nxt -match '^#'){ break }
      $heroLead = $nxt.Trim()
      $skipLine.Add($j) | Out-Null
      break
    }
    break
  }
}

# Build body HTML
$sb = New-Object System.Text.StringBuilder
$inList = $false
$inBenefits = $false
$inFaq = $false
$faqCount = 0

function Close-List {
  param([ref]$inList,[ref]$sb)
  if ($inList.Value){ [void]$sb.Value.AppendLine('</ul>'); $inList.Value = $false }
}

function Build-FormHtml([string]$formId, $spec, [string]$buttonText){
  $nameField = $false
  $emailLabel = 'メールアドレス'
  $nameLabel = 'お名前'
  $nameRequired = $false
  if ($spec -and $spec.fields -and $spec.fields.name){ $nameField = $true; if ($spec.fields.name.required){ $nameRequired = $true } }
  $consentHtml = ''
  if ($spec -and $spec.consent_checkbox){
    $cid = $spec.consent_checkbox.id
    if (-not $cid) { $cid = 'consent' }
    $clabel = $spec.consent_checkbox.label
    if (-not $clabel) { $clabel = 'プライバシーポリシーに同意します' }
    $consentHtml = ("<label class='consent-row'><input id='{0}-{1}' name='{0}' type='checkbox' required /> <span>{2}</span></label>" -f $cid, $formId, (Escape-Html $clabel))
  }
  $hiddenHtml = ''
  if ($spec -and $spec.hidden_from_url){
    foreach($k in $spec.hidden_from_url){ $hiddenHtml += ("<input type='hidden' name='{0}' data-from-url='1' />" -f $k) }
  }
  $attrs = ''
  if ($spec -and $spec.endpoint){ $attrs += (" data-endpoint='{0}'" -f $spec.endpoint) }
  if ($spec -and $spec.method){ $attrs += (" data-method='{0}'" -f $spec.method) }

  $form = @()
  $form += ("<form class='lead-form lead-form--lg' id='{0}'{1}>" -f $formId, $attrs)
  if ($nameField){
    $form += ("<label class='sr-only' for='name-{0}'>{1}</label>" -f $formId, $nameLabel)
    $req = if ($nameRequired) { ' required' } else { '' }
    $form += ("<input id='name-{0}' name='name' type='text' inputmode='text' placeholder='{1}'{2} />" -f $formId, $nameLabel, $req)
  }
  $form += ("<label class='sr-only' for='email-{0}'>{1}</label>" -f $formId, $emailLabel)
  $form += ("<input id='email-{0}' name='email' type='email' inputmode='email' enterkeyhint='go' autocomplete='email' autocapitalize='off' autocorrect='off' placeholder='{1}' required />" -f $formId, $emailLabel)
  $form += $consentHtml
  if ([string]::IsNullOrWhiteSpace($buttonText)) { $buttonText = '送信' }
  $form += ("<button type='submit' class='btn btn--primary btn--xl' data-cta='dynamic'>{0}</button>" -f (Escape-Html $buttonText))
  $form += $hiddenHtml
  $form += "</form>"
  return ($form -join "")
}

$formSpec = $null
if (Test-Path 'form_spec.json'){ $formSpec = Read-JsonSmart 'form_spec.json' }

$globalCtaLabel = '送信'

for ($i = 0; $i -lt $lines.Count; $i++){
  if ($skipLine.Contains($i)) { continue }
  $line = $lines[$i]

  if ($line -match '^##\s*CTA(\d+)'){ # insert CTA block
    Close-List -inList ([ref]$inList) -sb ([ref]$sb)
    $ctaNum = $Matches[1]
    $formId = "lead-form-cta$ctaNum"
    $anchor = if ($i -ge ($lines.Count-1)) { ' id="cta-bottom"' } else { '' }
    [void]$sb.AppendLine(("<section class='section cta' aria-label='CTA{0}'{1}>" -f $ctaNum, $anchor))
    [void]$sb.AppendLine('<div class="container">')
    $btnText = $null
    # Look ahead for a CTA label line like "CTA: xxx" or "ボタン: xxx"
    for ($k = $i+1; $k -lt $lines.Count; $k++){
      $nxt = $lines[$k]
      if ($nxt -match '^\s*$'){ continue }
      if ($nxt -match '^#'){ break }
      if ($nxt -match '^(CTA|ボタン)\s*[:：]\s*(.+)$'){
        $btnText = $Matches[2].Trim()
        $skipLine.Add($k) | Out-Null
      }
      break
    }
    if ($btnText -and $globalCtaLabel -eq '送信'){ $globalCtaLabel = $btnText }
    [void]$sb.AppendLine((Build-FormHtml -formId $formId -spec $formSpec -buttonText $btnText))
    [void]$sb.AppendLine('</div>')
    [void]$sb.AppendLine('</section>')
    continue
  }

  if ($line -match '^##\s*(.+)$'){
    # Close open feature blocks
    if ($inBenefits) { [void]$sb.AppendLine('</div>'); $inBenefits = $false }
    if ($inFaq) { [void]$sb.AppendLine('</div>'); $inFaq = $false }
    Close-List -inList ([ref]$inList) -sb ([ref]$sb)
    $h = $Matches[1].Trim()
    [void]$sb.AppendLine('<h2 class="section__title">'+(Escape-Html $h)+'</h2>')
    if ($h -match '(実績|ベネフィット|メリット|Benefit|Benefits)'){ [void]$sb.AppendLine('<div class="benefits">'); $inBenefits = $true; continue }
    if ($h -match '^(FAQ|よくある質問)$'){ [void]$sb.AppendLine('<div class="faq">'); $inFaq = $true; $faqCount = 0; continue }
    continue
  }
  if ($line -match '^###\s*(.+)$'){
    Close-List -inList ([ref]$inList) -sb ([ref]$sb)
    [void]$sb.AppendLine('<h3>'+(Escape-Html $Matches[1].Trim())+'</h3>')
    continue
  }
  # Markdown image: ![alt](path) — only allow ./assets/*
  if ($line -match '^!\[(.*?)\]\((.*?)\)'){ 
    $alt = (Escape-Html $Matches[1])
    $src = $Matches[2].Trim()
    if ($src -notmatch '^\.?/?assets/'){ 
      # Not allowed source, render a placeholder instead
      [void]$sb.AppendLine('<div class="img-ph" aria-hidden="true"></div>')
    } else {
      if ($src -notmatch '^\./'){ $src = './' + $src }
      [void]$sb.AppendLine('<figure class="md-img"><img src="'+$src+'" alt="'+$alt+'" /></figure>')
    }
    continue
  }
  if ($line -match '^\s*$'){
    Close-List -inList ([ref]$inList) -sb ([ref]$sb)
    continue
  }
  if ($line -match '^(\-|\*|・)\s*(.+)$'){
    if ($inFaq) { Close-List -inList ([ref]$inList) -sb ([ref]$sb) }
    if ($inBenefits){
      $txt = Escape-Html ($Matches[2].Trim())
      [void]$sb.AppendLine('<div class="benefit-item"><div class="benefit-bullet"></div><div class="benefit-text">'+$txt+'</div></div>')
      continue
    }
    if (-not $inList){ [void]$sb.AppendLine('<ul>'); $inList = $true }
    [void]$sb.AppendLine('<li>'+(Escape-Html $Matches[2].Trim())+'</li>')
    continue
  }

  # FAQ Q/A detection: Q: ... then answer lines until blank or next heading/Q
  if ($inFaq -and ($line -match '^Q[：:．\.、]\s*(.+)$')){
    $q = Escape-Html ($Matches[1].Trim())
    $faqCount++
    $pid = 'faq-a-'+$faqCount
    # collect answer
    $ansSb = New-Object System.Text.StringBuilder
    for ($j=$i+1; $j -lt $lines.Count; $j++){
      $n = $lines[$j]
      if ($n -match '^\s*$'){ $skipLine.Add($j) | Out-Null; break }
      if ($n -match '^#' -or $n -match '^Q[：:．\.、]'){ break }
      $skipLine.Add($j) | Out-Null
      [void]$ansSb.AppendLine('<p>'+ (Escape-Html ($n.Trim())) +'</p>')
    }
    [void]$sb.AppendLine('<div class="faq-item">')
    [void]$sb.AppendLine('<button class="faq-q" type="button" data-faq-toggle aria-expanded="false" aria-controls="'+$pid+'">'+$q+' <span class="faq-icon">＋</span></button>')
    [void]$sb.AppendLine('<div class="faq-a" id="'+$pid+'" hidden>')
    [void]$sb.AppendLine($ansSb.ToString())
    [void]$sb.AppendLine('</div>')
    [void]$sb.AppendLine('</div>')
    continue
  }

  # paragraph line
  $text = Escape-Html ($line.Trim())
  [void]$sb.AppendLine('<p>'+ $text +'</p>')
}
Close-List -inList ([ref]$inList) -sb ([ref]$sb)

# Inject into template
if ([string]::IsNullOrWhiteSpace($heroTitle)) { $heroTitle = '' }
if ([string]::IsNullOrWhiteSpace($heroLead)) { $heroLead = '' }

$outHtml = $templateHtml.Replace('{{HERO_TITLE}}', (Escape-Html $heroTitle)).Replace('{{HERO_LEAD}}', (Escape-Html $heroLead))

# CTA label injection for header/sticky buttons
$outHtml = $outHtml.Replace('{{CTA_LABEL}}', (Escape-Html $globalCtaLabel))

# Replace MD block between markers
$pattern = '<!-- MD:START -->[\s\S]*?<!-- MD:END -->'
$replacement = '<!-- MD:START -->' + "`n" + $sb.ToString() + '<!-- MD:END -->'
$outHtml = [System.Text.RegularExpressions.Regex]::Replace($outHtml, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $replacement })

# Assets: logo, favicons, hero image
$assetHead = ''
$brandHtml = '<div class="brand">BRAND</div>'
if (Test-Path 'assets') {
  # Copy assets into dist/img
  if (-not (Test-Path (Join-Path $OutDir 'img'))) { New-Item -ItemType Directory -Path (Join-Path $OutDir 'img') | Out-Null }
  Copy-Item 'assets/*' (Join-Path $OutDir 'img') -Force -Recurse -ErrorAction SilentlyContinue

  # Choose logo
  $logo = Get-ChildItem 'assets' -File -Include 'logo.svg','logo.png','logo.jpg','logo.jpeg','logo.webp' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($logo) {
    $brandHtml = '<a class="brand" href="#"><img src="./img/'+ $logo.Name +'" alt="Brand" /></a>'
  }

  # Favicons
  $apple = Get-ChildItem 'assets' -File -Include 'apple-touch-icon.png' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($apple) { $assetHead += '<link rel="apple-touch-icon" href="./assets/'+$apple.Name+'" />' + "`n" }
  $ico = Get-ChildItem 'assets' -File -Include 'favicon.ico' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($ico) { $assetHead += '<link rel="icon" href="./assets/'+$ico.Name+'" sizes="any" />' + "`n" }
  $svg = Get-ChildItem 'assets' -File -Include 'favicon.svg' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($svg) { $assetHead += '<link rel="icon" href="./assets/'+$svg.Name+'" type="image/svg+xml" />' + "`n" }
  $pngFav = Get-ChildItem 'assets' -File -Include 'favicon.png' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($pngFav) { $assetHead += '<link rel="icon" href="./assets/'+$pngFav.Name+'" type="image/png" />' + "`n" }

  # Hero image (assets/hero.*)
  $hero = Get-ChildItem 'assets' -File -Include 'hero.webp','hero.png','hero.jpg','hero.jpeg' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($hero) {
    $heroPath = ('./img/' + $hero.Name)
    $heroPathEsc = $heroPath -replace "'", '%27'
    $assetHead += ("<link rel='preload' as='image' href='{0}' />`n" -f $heroPath)
    $assetHead += ("<style>:root{--hero-bg:url('{0}')}</style>`n" -f $heroPathEsc)
  }
}

# Inject assets
$outHtml = $outHtml.Replace('{{BRAND}}', $brandHtml)
$outHtml = $outHtml.Replace('<!-- ASSET_HEAD -->', $assetHead)

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

# Adjust asset paths for dist structure
$outHtml = $outHtml -replace 'href="styles\.css"','href="./css/styles.css"'
$outHtml = $outHtml -replace 'src="main\.js"','src="./js/main.js"'
# Replace any ./assets/ image refs in generated content to ./img/
$outHtml = $outHtml -replace 'src="\./assets/','src="./img/'

# Write files
Set-Content -LiteralPath (Join-Path $OutDir 'index.html') -Value $outHtml -NoNewline -Encoding UTF8

# Create output folders
if (-not (Test-Path (Join-Path $OutDir 'css'))) { New-Item -ItemType Directory -Path (Join-Path $OutDir 'css') | Out-Null }
if (-not (Test-Path (Join-Path $OutDir 'js'))) { New-Item -ItemType Directory -Path (Join-Path $OutDir 'js') | Out-Null }

# Copy static assets into folder structure
Copy-Item styles.css (Join-Path $OutDir 'css/styles.css') -Force
Copy-Item main.js (Join-Path $OutDir 'js/main.js') -Force
# Avoid copying root-level images to prevent leaking reference assets
if (Test-Path 'ref') {
  if (-not (Test-Path (Join-Path $OutDir 'ref'))) { New-Item -ItemType Directory -Path (Join-Path $OutDir 'ref') | Out-Null }
  Copy-Item 'ref/*' (Join-Path $OutDir 'ref') -Force -ErrorAction SilentlyContinue
}
if (Test-Path 'form_spec.json') {
  Copy-Item 'form_spec.json' (Join-Path $OutDir 'form_spec.json') -Force -ErrorAction SilentlyContinue
  # Also inline a small config for environments where fetch of local file is restricted
  $specRaw = Get-Content -LiteralPath 'form_spec.json' -Raw -Encoding UTF8
  $inline = '<script>window.FORM_SPEC = '+ $specRaw +';</script>'
  (Get-Content -LiteralPath (Join-Path $OutDir 'index.html') -Raw -Encoding UTF8).Replace('</head>', ($inline+"`n</head>")) | Set-Content -LiteralPath (Join-Path $OutDir 'index.html') -NoNewline -Encoding UTF8
}

# Generate simple thanks page if specified
if ($formSpec -and $formSpec.success_redirect) {
  $thanks = @()
  $thanks += '<!doctype html>'
  $thanks += '<meta charset="utf-8" />'
  $thanks += '<meta name="viewport" content="width=device-width, initial-scale=1" />'
  $thanks += '<link rel="stylesheet" href="./styles.css" />'
  $thanks += '<div class="container section"><h1 class="section__title">ご登録ありがとうございます</h1><p>確認メールを送信しました。数分たっても届かない場合は迷惑メールをご確認ください。</p></div>'
  Set-Content -LiteralPath (Join-Path $OutDir 'thanks.html') -Value ($thanks -join "") -NoNewline -Encoding UTF8
}

Write-Host "Built -> $OutDir/index.html"

