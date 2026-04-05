# S19.6 Manual Tutorial - [scripts/smoke-test-cogmem.ps1](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/smoke-test-cogmem.ps1)

## Purpose
- Smoke test retain/recall cho CogMem API bằng PowerShell.
- Kiểm chứng nhanh hợp đồng API cơ bản sau khi khởi chạy dịch vụ.

## Source File
- [scripts/smoke-test-cogmem.ps1](https://github.com/triet4p/agent-memory-cognitive/blob/master/scripts/smoke-test-cogmem.ps1)

## Symbol-by-symbol explanation
### param($BaseUrl)
- Cho phép truyền base URL API, mặc định http://localhost:8888.

### $bankId
- Tạo bank id riêng theo PID để tránh va chạm giữa các lần test.

### Retain block
- Gọi POST /v1/default/banks/{bankId}/memories với một item mẫu.
- Kiểm tra retainResponse.success phải là true.

### Recall block
- Gọi POST /v1/default/banks/{bankId}/memories/recall với query mẫu.
- Kiểm tra results count > 0.

### PASS output
- In thông báo PASS khi cả retain và recall đều đạt.

### Symbol inventory bổ sung (full names)
- $ErrorActionPreference, $retainBody, $retainResponse, $recallBody, $recallResponse, $resultsCount

## Cross-file dependencies (inbound/outbound)
### Inbound callers
- [docker/test-image.ps1](https://github.com/triet4p/agent-memory-cognitive/blob/master/docker/test-image.ps1) gọi script này sau khi health check pass.
- Người vận hành có thể gọi trực tiếp khi debug local.

### Outbound dependencies
- CogMem API endpoints /memories và /memories/recall.
- PowerShell cmdlet Invoke-RestMethod.

## Runtime implications/side effects
- Tạo dữ liệu nhớ tạm trong bank smoke id mới mỗi lần chạy.
- Không có bước cleanup bank trong script này.

## Failure modes
- API không sẵn sàng hoặc endpoint đổi contract.
- retain success=false hoặc recall không trả result.
- BaseUrl sai dẫn tới lỗi kết nối.

## Verify commands
```powershell
pwsh -NoProfile -Command "$null=$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile('scripts/smoke-test-cogmem.ps1',[ref]$tokens,[ref]$errors) | Out-Null; if($errors.Count -gt 0){$errors | ForEach-Object { $_.ToString() }; exit 1}; 'OK'"
pwsh -NoProfile -File scripts/smoke-test-cogmem.ps1 -BaseUrl http://localhost:8888
```

