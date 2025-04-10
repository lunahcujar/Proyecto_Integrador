for ($i = 1; $i -le 10; $i++) {
    if ($i -eq 1 -or $i -eq 9) { continue }  # Saltar la iteración cuando $i sea 1 o 9
    Write-Host "Valor: $i"
}
