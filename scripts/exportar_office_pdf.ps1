param(
    [string]$DocxPath = "",
    [string]$DocxPdfPath = "",
    [string]$PptxPath = "",
    [string]$PptxPdfPath = "",
    [string]$SlidesPngDir = ""
)

$ErrorActionPreference = "Stop"

if ($DocxPath -ne "" -and $DocxPdfPath -ne "") {
    $word = $null
    $doc = $null
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $word.DisplayAlerts = 0
        $doc = $word.Documents.Open($DocxPath, $false, $true)
        $doc.SaveAs([ref]$DocxPdfPath, [ref]17)
        Write-Host "WORD_PDF_OK: $DocxPdfPath"
    }
    finally {
        if ($doc -ne $null) { $doc.Close([ref]$false); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
        if ($word -ne $null) { $word.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    }
}

if ($PptxPath -ne "" -and $PptxPdfPath -ne "") {
    $ppt = $null
    $pres = $null
    try {
        $ppt = New-Object -ComObject PowerPoint.Application
        $pres = $ppt.Presentations.Open($PptxPath, $true, $false, $false)
        $pres.SaveAs($PptxPdfPath, 32)
        Write-Host "PPT_PDF_OK: $PptxPdfPath"

        if ($SlidesPngDir -ne "") {
            if (-not (Test-Path $SlidesPngDir)) {
                New-Item -ItemType Directory -Force -Path $SlidesPngDir | Out-Null
            }
            $idx = 1
            foreach ($slide in $pres.Slides) {
                $pngName = "slide_{0:D2}.png" -f $idx
                $pngPath = Join-Path $SlidesPngDir $pngName
                $slide.Export($pngPath, "PNG", 1920, 1080)
                $idx++
            }
            Write-Host "PPT_PNGS_OK: $($idx - 1) slides em $SlidesPngDir"
        }
    }
    finally {
        if ($pres -ne $null) { $pres.Close(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) }
        if ($ppt -ne $null) { $ppt.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) }
    }
}
