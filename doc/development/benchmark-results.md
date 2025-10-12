# Benchmark results

## Nvidia GPU acceleration

not yet tested

## OpenVino CPU+GPU+NPU acceleration

### Test 1: On a Linux AMD CPU

As expected no speedup over regular CPU version

Test config:
CPU: AMD Ryzen 9 5950X 16-Core Processor
RAM: 32GB
GPU: AMD Navi 31 [Radeon RX 7900 XT/7900 XTX/7900 GRE/7900M] (rev ce)

kevinh@kdesktop:~/development/telescope/graxpert$ pipx install dist/graxpert-3.2.0a0.dev2-py3-none-any.whl[openvino]
  installed package graxpert 3.2.0a0.dev2, installed using Python 3.12.3
  These apps are now globally available
    - graxpert
done! ✨ 🌟 ✨
kevinh@kdesktop:~/development/telescope/graxpert$ graxpert -cmd background-extraction -output /tmp/testout tests/test_images/real_crummy.fits
2025-09-13 00:00:31,850 MainProcess root INFO     Starting GraXpert CLI, Background-Extraction, version: 3.2.0a0.dev2 release: 1
2025-09-13 00:00:32,018 MainProcess root INFO     Using stored smoothing value 0.0.
2025-09-13 00:00:32,018 MainProcess root INFO     Using stored correction type Subtraction.
2025-09-13 00:00:32,018 MainProcess root INFO     Using stored gpu acceleration setting True.
2025-09-13 00:00:32,519 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-13 00:00:32,520 MainProcess root INFO     Excecuting background extraction with the following parameters:
interpolation type - AI
         smoothing - 0.0
   correction type - Subtraction
     AI model path - /home/kevinh/.local/share/GraXpert/bge-ai-models/1.0.1/model.onnx
2025-09-13 00:00:33,287 MainProcess root INFO     Providers : [('OpenVINOExecutionProvider', {'device_type': 'AUTO'}), 'CPUExecutionProvider']
2025-09-13 00:00:33,287 MainProcess root INFO     Used providers : ['OpenVINOExecutionProvider', 'CPUExecutionProvider']
kevinh@kdesktop:~/development/telescope/graxpert$ ./benchmark.sh 
Running background extraction...
2025-09-13 00:01:18,767 MainProcess root INFO     Starting GraXpert CLI, Background-Extraction, version: 3.2.0a0.dev2 release: 1
2025-09-13 00:01:18,933 MainProcess root INFO     Using stored smoothing value 0.0.
2025-09-13 00:01:18,933 MainProcess root INFO     Using stored correction type Subtraction.
2025-09-13 00:01:18,933 MainProcess root INFO     Using user-supplied gpu acceleration setting True.
2025-09-13 00:01:19,436 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-13 00:01:19,436 MainProcess root INFO     Excecuting background extraction with the following parameters:
interpolation type - AI
         smoothing - 0.0
   correction type - Subtraction
     AI model path - /home/kevinh/.local/share/GraXpert/bge-ai-models/1.0.1/model.onnx
2025-09-13 00:01:20,171 MainProcess root INFO     Providers : [('OpenVINOExecutionProvider', {'device_type': 'AUTO'}), 'CPUExecutionProvider']
2025-09-13 00:01:20,171 MainProcess root INFO     Used providers : ['OpenVINOExecutionProvider', 'CPUExecutionProvider']

real	0m6.076s
user	0m7.241s
sys	0m1.315s
Running deconvolution (object)...
2025-09-13 00:01:24,886 MainProcess root INFO     Starting GraXpert CLI, Deconvolution Obj, version: 3.2.0a0.dev2 release: 1
2025-09-13 00:01:24,939 MainProcess root INFO     Using stored deconvolution strength value 0.5.
2025-09-13 00:01:24,939 MainProcess root INFO     Using stored deconvolution psfsize value 5.0.
2025-09-13 00:01:24,939 MainProcess root INFO     Using stored batch size value 4.
2025-09-13 00:01:24,939 MainProcess root INFO     Using user-supplied gpu acceleration setting True.
2025-09-13 00:01:25,441 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-13 00:01:25,442 MainProcess root INFO     Excecuting deconvolution on objects with the following parameters:
AI model path - /home/kevinh/.local/share/GraXpert/deconvolution-object-ai-models/1.0.1/model.onnx
deconvolution strength - 0.5
deconvolution psfsize - 5.0
2025-09-13 00:01:25,442 MainProcess root INFO     Starting deconvolution
2025-09-13 00:01:25,442 MainProcess root INFO     Calculated normalized PSFsize value: 0.2951167728237792
2025-09-13 00:01:26,587 MainProcess root INFO     Available inference providers : [('OpenVINOExecutionProvider', {'device_type': 'AUTO'}), 'CPUExecutionProvider']
2025-09-13 00:01:26,587 MainProcess root INFO     Used inference providers : ['OpenVINOExecutionProvider', 'CPUExecutionProvider']
2025-09-13 00:01:30,344 MainProcess root INFO     Progress: 1%
2025-09-13 00:01:32,223 MainProcess root INFO     Progress: 3%
2025-09-13 00:01:34,125 MainProcess root INFO     Progress: 4%
2025-09-13 00:01:36,326 MainProcess root INFO     Progress: 6%
2025-09-13 00:01:38,533 MainProcess root INFO     Progress: 7%
2025-09-13 00:01:40,745 MainProcess root INFO     Progress: 9%
2025-09-13 00:01:42,630 MainProcess root INFO     Progress: 10%
2025-09-13 00:01:44,526 MainProcess root INFO     Progress: 12%
2025-09-13 00:01:46,815 MainProcess root INFO     Progress: 14%
2025-09-13 00:01:49,023 MainProcess root INFO     Progress: 15%
2025-09-13 00:01:50,939 MainProcess root INFO     Progress: 17%
2025-09-13 00:01:52,910 MainProcess root INFO     Progress: 18%
2025-09-13 00:01:55,158 MainProcess root INFO     Progress: 20%
2025-09-13 00:01:57,381 MainProcess root INFO     Progress: 21%
2025-09-13 00:01:59,288 MainProcess root INFO     Progress: 23%
2025-09-13 00:02:01,129 MainProcess root INFO     Progress: 25%
2025-09-13 00:02:02,996 MainProcess root INFO     Progress: 26%
2025-09-13 00:02:04,974 MainProcess root INFO     Progress: 28%
2025-09-13 00:02:06,813 MainProcess root INFO     Progress: 29%
2025-09-13 00:02:08,686 MainProcess root INFO     Progress: 31%
2025-09-13 00:02:10,596 MainProcess root INFO     Progress: 32%
2025-09-13 00:02:12,446 MainProcess root INFO     Progress: 34%
2025-09-13 00:02:14,310 MainProcess root INFO     Progress: 35%
2025-09-13 00:02:16,203 MainProcess root INFO     Progress: 37%
2025-09-13 00:02:18,093 MainProcess root INFO     Progress: 39%
2025-09-13 00:02:20,266 MainProcess root INFO     Progress: 40%
2025-09-13 00:02:22,166 MainProcess root INFO     Progress: 42%
2025-09-13 00:02:24,034 MainProcess root INFO     Progress: 43%
2025-09-13 00:02:26,238 MainProcess root INFO     Progress: 45%
2025-09-13 00:02:28,132 MainProcess root INFO     Progress: 46%
2025-09-13 00:02:30,350 MainProcess root INFO     Progress: 48%
2025-09-13 00:02:32,578 MainProcess root INFO     Progress: 50%
2025-09-13 00:02:34,448 MainProcess root INFO     Progress: 51%
2025-09-13 00:02:36,671 MainProcess root INFO     Progress: 53%
2025-09-13 00:02:38,892 MainProcess root INFO     Progress: 54%
2025-09-13 00:02:40,743 MainProcess root INFO     Progress: 56%
2025-09-13 00:02:42,631 MainProcess root INFO     Progress: 57%
2025-09-13 00:02:44,542 MainProcess root INFO     Progress: 59%
2025-09-13 00:02:46,428 MainProcess root INFO     Progress: 60%
2025-09-13 00:02:48,272 MainProcess root INFO     Progress: 62%
2025-09-13 00:02:50,162 MainProcess root INFO     Progress: 64%
2025-09-13 00:02:52,047 MainProcess root INFO     Progress: 65%
2025-09-13 00:02:53,943 MainProcess root INFO     Progress: 67%
2025-09-13 00:02:55,825 MainProcess root INFO     Progress: 68%
2025-09-13 00:02:58,049 MainProcess root INFO     Progress: 70%
2025-09-13 00:02:59,997 MainProcess root INFO     Progress: 71%
2025-09-13 00:03:02,228 MainProcess root INFO     Progress: 73%
2025-09-13 00:03:04,454 MainProcess root INFO     Progress: 75%
2025-09-13 00:03:06,347 MainProcess root INFO     Progress: 76%
2025-09-13 00:03:08,226 MainProcess root INFO     Progress: 78%
2025-09-13 00:03:10,097 MainProcess root INFO     Progress: 79%
2025-09-13 00:03:12,309 MainProcess root INFO     Progress: 81%
2025-09-13 00:03:14,552 MainProcess root INFO     Progress: 82%
2025-09-13 00:03:16,823 MainProcess root INFO     Progress: 84%
2025-09-13 00:03:18,693 MainProcess root INFO     Progress: 85%
2025-09-13 00:03:20,578 MainProcess root INFO     Progress: 87%
2025-09-13 00:03:22,517 MainProcess root INFO     Progress: 89%
2025-09-13 00:03:24,378 MainProcess root INFO     Progress: 90%
2025-09-13 00:03:26,627 MainProcess root INFO     Progress: 92%
2025-09-13 00:03:28,943 MainProcess root INFO     Progress: 93%
2025-09-13 00:03:31,232 MainProcess root INFO     Progress: 95%
2025-09-13 00:03:33,451 MainProcess root INFO     Progress: 96%
2025-09-13 00:03:33,510 MainProcess root INFO     Finished deconvolution

real	2m13.279s
user	30m4.238s
sys	0m3.152s
Running denoising...
2025-09-13 00:03:38,137 MainProcess root INFO     Starting GraXpert CLI, Denoising, version: 3.2.0a0.dev2 release: 1
2025-09-13 00:03:38,190 MainProcess root INFO     Using stored denoise strength value 0.5.
2025-09-13 00:03:38,191 MainProcess root INFO     Using stored batch size value 4.
2025-09-13 00:03:38,191 MainProcess root INFO     Using user-supplied gpu acceleration setting True.
2025-09-13 00:03:39,368 MainProcess root INFO     Using AI version 3.0.2. You can overwrite this by providing the argument '-ai_version'
2025-09-13 00:03:39,369 MainProcess root INFO     Excecuting denoising with the following parameters:
AI model path - /home/kevinh/.local/share/GraXpert/denoise-ai-models/3.0.2/model.onnx
denoise strength - 0.5
2025-09-13 00:03:39,369 MainProcess root INFO     Starting denoising
2025-09-13 00:03:41,274 MainProcess root INFO     Available inference providers : [('OpenVINOExecutionProvider', {'device_type': 'AUTO'}), 'CPUExecutionProvider']
2025-09-13 00:03:41,274 MainProcess root INFO     Used inference providers : ['OpenVINOExecutionProvider', 'CPUExecutionProvider']
2025-09-13 00:03:55,251 MainProcess root INFO     Progress: 1%
2025-09-13 00:04:04,501 MainProcess root INFO     Progress: 2%
2025-09-13 00:04:13,946 MainProcess root INFO     Progress: 3%
2025-09-13 00:04:23,322 MainProcess root INFO     Progress: 4%
2025-09-13 00:04:32,848 MainProcess root INFO     Progress: 5%
2025-09-13 00:04:37,693 MainProcess root INFO     Progress: 6%
2025-09-13 00:04:47,868 MainProcess root INFO     Progress: 7%
2025-09-13 00:04:57,753 MainProcess root INFO     Progress: 8%
2025-09-13 00:05:07,638 MainProcess root INFO     Progress: 9%
2025-09-13 00:05:17,102 MainProcess root INFO     Progress: 10%
2025-09-13 00:05:26,265 MainProcess root INFO     Progress: 11%
2025-09-13 00:05:30,851 MainProcess root INFO     Progress: 12%
2025-09-13 00:05:40,037 MainProcess root INFO     Progress: 13%
2025-09-13 00:05:49,413 MainProcess root INFO     Progress: 14%
2025-09-13 00:05:58,863 MainProcess root INFO     Progress: 15%
2025-09-13 00:06:08,024 MainProcess root INFO     Progress: 16%
2025-09-13 00:06:12,645 MainProcess root INFO     Progress: 17%
2025-09-13 00:06:22,058 MainProcess root INFO     Progress: 18%
2025-09-13 00:06:31,288 MainProcess root INFO     Progress: 19%
2025-09-13 00:06:40,649 MainProcess root INFO     Progress: 20%
2025-09-13 00:06:49,847 MainProcess root INFO     Progress: 21%
2025-09-13 00:06:59,183 MainProcess root INFO     Progress: 22%
2025-09-13 00:07:03,893 MainProcess root INFO     Progress: 23%
2025-09-13 00:07:13,304 MainProcess root INFO     Progress: 24%
2025-09-13 00:07:22,505 MainProcess root INFO     Progress: 25%
2025-09-13 00:07:31,831 MainProcess root INFO     Progress: 26%
2025-09-13 00:07:41,022 MainProcess root INFO     Progress: 27%
2025-09-13 00:07:50,270 MainProcess root INFO     Progress: 28%
2025-09-13 00:07:55,011 MainProcess root INFO     Progress: 29%
2025-09-13 00:08:04,421 MainProcess root INFO     Progress: 30%
2025-09-13 00:08:14,169 MainProcess root INFO     Progress: 31%
2025-09-13 00:08:24,114 MainProcess root INFO     Progress: 32%
2025-09-13 00:08:33,899 MainProcess root INFO     Progress: 33%
2025-09-13 00:08:38,428 MainProcess root INFO     Progress: 34%
2025-09-13 00:08:47,617 MainProcess root INFO     Progress: 35%
2025-09-13 00:08:56,776 MainProcess root INFO     Progress: 36%
2025-09-13 00:09:06,026 MainProcess root INFO     Progress: 37%
2025-09-13 00:09:15,207 MainProcess root INFO     Progress: 38%
2025-09-13 00:09:24,759 MainProcess root INFO     Progress: 39%
2025-09-13 00:09:29,352 MainProcess root INFO     Progress: 40%
2025-09-13 00:09:38,889 MainProcess root INFO     Progress: 41%
2025-09-13 00:09:48,306 MainProcess root INFO     Progress: 42%
2025-09-13 00:09:57,710 MainProcess root INFO     Progress: 43%
2025-09-13 00:10:07,153 MainProcess root INFO     Progress: 44%
2025-09-13 00:10:16,448 MainProcess root INFO     Progress: 45%
2025-09-13 00:10:21,193 MainProcess root INFO     Progress: 46%
2025-09-13 00:10:30,811 MainProcess root INFO     Progress: 47%
2025-09-13 00:10:40,306 MainProcess root INFO     Progress: 48%
2025-09-13 00:10:49,611 MainProcess root INFO     Progress: 49%
2025-09-13 00:10:59,275 MainProcess root INFO     Progress: 50%
2025-09-13 00:11:04,127 MainProcess root INFO     Progress: 51%
2025-09-13 00:11:13,252 MainProcess root INFO     Progress: 52%
2025-09-13 00:11:22,677 MainProcess root INFO     Progress: 53%
2025-09-13 00:11:32,093 MainProcess root INFO     Progress: 54%
2025-09-13 00:11:41,534 MainProcess root INFO     Progress: 55%
2025-09-13 00:11:51,118 MainProcess root INFO     Progress: 56%
2025-09-13 00:11:55,753 MainProcess root INFO     Progress: 57%
2025-09-13 00:12:05,287 MainProcess root INFO     Progress: 58%
2025-09-13 00:12:14,595 MainProcess root INFO     Progress: 59%
2025-09-13 00:12:23,962 MainProcess root INFO     Progress: 60%
2025-09-13 00:12:33,593 MainProcess root INFO     Progress: 61%
2025-09-13 00:12:38,498 MainProcess root INFO     Progress: 62%
2025-09-13 00:12:47,819 MainProcess root INFO     Progress: 63%
2025-09-13 00:12:57,705 MainProcess root INFO     Progress: 64%
2025-09-13 00:13:06,872 MainProcess root INFO     Progress: 65%
2025-09-13 00:13:16,056 MainProcess root INFO     Progress: 66%
2025-09-13 00:13:25,120 MainProcess root INFO     Progress: 67%
2025-09-13 00:13:29,668 MainProcess root INFO     Progress: 68%
2025-09-13 00:13:38,703 MainProcess root INFO     Progress: 69%
2025-09-13 00:13:47,808 MainProcess root INFO     Progress: 70%
2025-09-13 00:13:57,052 MainProcess root INFO     Progress: 71%
2025-09-13 00:14:06,226 MainProcess root INFO     Progress: 72%
2025-09-13 00:14:15,444 MainProcess root INFO     Progress: 73%
2025-09-13 00:14:20,162 MainProcess root INFO     Progress: 74%
2025-09-13 00:14:29,218 MainProcess root INFO     Progress: 75%
2025-09-13 00:14:38,319 MainProcess root INFO     Progress: 76%
2025-09-13 00:14:47,382 MainProcess root INFO     Progress: 77%
2025-09-13 00:14:56,394 MainProcess root INFO     Progress: 78%
2025-09-13 00:15:00,932 MainProcess root INFO     Progress: 79%
2025-09-13 00:15:10,029 MainProcess root INFO     Progress: 80%
2025-09-13 00:15:19,093 MainProcess root INFO     Progress: 81%
2025-09-13 00:15:28,148 MainProcess root INFO     Progress: 82%
2025-09-13 00:15:37,273 MainProcess root INFO     Progress: 83%
2025-09-13 00:15:46,333 MainProcess root INFO     Progress: 84%
2025-09-13 00:15:51,035 MainProcess root INFO     Progress: 85%
2025-09-13 00:16:00,339 MainProcess root INFO     Progress: 86%
2025-09-13 00:16:09,579 MainProcess root INFO     Progress: 87%
2025-09-13 00:16:18,638 MainProcess root INFO     Progress: 88%
2025-09-13 00:16:27,698 MainProcess root INFO     Progress: 89%
2025-09-13 00:16:36,939 MainProcess root INFO     Progress: 90%
2025-09-13 00:16:41,469 MainProcess root INFO     Progress: 91%
2025-09-13 00:16:50,719 MainProcess root INFO     Progress: 92%
2025-09-13 00:16:59,786 MainProcess root INFO     Progress: 93%
2025-09-13 00:17:09,000 MainProcess root INFO     Progress: 94%
2025-09-13 00:17:18,209 MainProcess root INFO     Progress: 95%
2025-09-13 00:17:22,781 MainProcess root INFO     Progress: 96%
2025-09-13 00:17:31,874 MainProcess root INFO     Progress: 97%
2025-09-13 00:17:40,910 MainProcess root INFO     Progress: 98%
2025-09-13 00:17:46,211 MainProcess root INFO     Progress: 99%
2025-09-13 00:17:46,536 MainProcess root INFO     Finished denoising

real	14m13.062s
user	216m52.417s
sys	0m6.549s

### Test 2: On a Windows Intel CPU (with openvino off)

Minix Z300 minipc with N300 CPU.

Very slow/low end CPU/GPU/APU combo, so only testing Deconvolution.

Walltime from python log was 7:50 minutes.

### Test 3: On a Windows Intel CPU/low-end GPU with openvino

About 1.5 minutes if I use the GPU in this low end machine.  So about a 5x speedup.

PS C:\Users\kevin\My Documents> graxpert -cmd deconv-obj -output c:\users\kevin\temp real_crummy.fits 
2025-09-12 19:08:44,607 MainProcess root INFO     Starting GraXpert CLI, Deconvolution Obj, version: 3.2.0a0.dev3 release: 1
2025-09-12 19:08:45,015 MainProcess root INFO     Using stored deconvolution strength value 0.5.
2025-09-12 19:08:45,016 MainProcess root INFO     Using stored deconvolution psfsize value 5.0.
2025-09-12 19:08:45,016 MainProcess root INFO     Using stored batch size value 4.
2025-09-12 19:08:45,017 MainProcess root INFO     Using stored gpu acceleration setting True.
2025-09-12 19:08:45,534 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-12 19:08:45,538 MainProcess root INFO     Excecuting deconvolution on objects with the following parameters:
AI model path - C:\Users\kevin\AppData\Local\GraXpert\GraXpert\deconvolution-object-ai-models\1.0.1\model.onnx
deconvolution strength - 0.5
deconvolution psfsize - 5.0
2025-09-12 19:08:45,538 MainProcess root INFO     Starting deconvolution
2025-09-12 19:08:45,539 MainProcess root INFO     Calculated normalized PSFsize value: 0.2951167728237792
2025-09-12 19:08:57,254 MainProcess root INFO     Available inference providers : [('OpenVINOExecutionProvider', {'device_type': 'GPU'}), 'CPUExecutionProvider']
2025-09-12 19:08:57,254 MainProcess root INFO     Used inference providers : ['OpenVINOExecutionProvider', 'CPUExecutionProvider']
2025-09-12 19:09:25,649 MainProcess root INFO     Progress: 1%
2025-09-12 19:09:27,387 MainProcess root INFO     Progress: 3%
2025-09-12 19:09:29,131 MainProcess root INFO     Progress: 4%
2025-09-12 19:09:30,883 MainProcess root INFO     Progress: 6%
2025-09-12 19:09:32,643 MainProcess root INFO     Progress: 7%
2025-09-12 19:09:34,404 MainProcess root INFO     Progress: 9%
2025-09-12 19:09:36,147 MainProcess root INFO     Progress: 10%
2025-09-12 19:09:38,073 MainProcess root INFO     Progress: 12%
2025-09-12 19:09:40,052 MainProcess root INFO     Progress: 14%
2025-09-12 19:09:41,975 MainProcess root INFO     Progress: 15%
2025-09-12 19:09:43,908 MainProcess root INFO     Progress: 17%
2025-09-12 19:09:45,822 MainProcess root INFO     Progress: 18%
2025-09-12 19:09:47,707 MainProcess root INFO     Progress: 20%
2025-09-12 19:09:49,600 MainProcess root INFO     Progress: 21%
2025-09-12 19:09:51,494 MainProcess root INFO     Progress: 23%
2025-09-12 19:09:53,394 MainProcess root INFO     Progress: 25%
2025-09-12 19:09:55,292 MainProcess root INFO     Progress: 26%
2025-09-12 19:09:57,184 MainProcess root INFO     Progress: 28%
2025-09-12 19:09:59,084 MainProcess root INFO     Progress: 29%
2025-09-12 19:10:00,991 MainProcess root INFO     Progress: 31%
2025-09-12 19:10:02,877 MainProcess root INFO     Progress: 32%
2025-09-12 19:10:04,781 MainProcess root INFO     Progress: 34%
2025-09-12 19:10:06,679 MainProcess root INFO     Progress: 35%
2025-09-12 19:10:08,577 MainProcess root INFO     Progress: 37%
2025-09-12 19:10:10,481 MainProcess root INFO     Progress: 39%
2025-09-12 19:10:12,376 MainProcess root INFO     Progress: 40%
2025-09-12 19:10:14,268 MainProcess root INFO     Progress: 42%
2025-09-12 19:10:16,172 MainProcess root INFO     Progress: 43%
2025-09-12 19:10:18,143 MainProcess root INFO     Progress: 45%
2025-09-12 19:10:20,042 MainProcess root INFO     Progress: 46%
2025-09-12 19:10:21,939 MainProcess root INFO     Progress: 48%
2025-09-12 19:10:23,825 MainProcess root INFO     Progress: 50%
2025-09-12 19:10:25,717 MainProcess root INFO     Progress: 51%
2025-09-12 19:10:27,605 MainProcess root INFO     Progress: 53%
2025-09-12 19:10:29,528 MainProcess root INFO     Progress: 54%
2025-09-12 19:10:31,425 MainProcess root INFO     Progress: 56%
2025-09-12 19:10:33,314 MainProcess root INFO     Progress: 57%
2025-09-12 19:10:35,213 MainProcess root INFO     Progress: 59%
2025-09-12 19:10:37,107 MainProcess root INFO     Progress: 60%
2025-09-12 19:10:39,002 MainProcess root INFO     Progress: 62%
2025-09-12 19:10:40,879 MainProcess root INFO     Progress: 64%
2025-09-12 19:10:42,755 MainProcess root INFO     Progress: 65%
2025-09-12 19:10:44,655 MainProcess root INFO     Progress: 67%
2025-09-12 19:10:46,561 MainProcess root INFO     Progress: 68%
2025-09-12 19:10:48,454 MainProcess root INFO     Progress: 70%
2025-09-12 19:10:50,360 MainProcess root INFO     Progress: 71%
2025-09-12 19:10:52,255 MainProcess root INFO     Progress: 73%
2025-09-12 19:10:54,134 MainProcess root INFO     Progress: 75%
2025-09-12 19:10:56,013 MainProcess root INFO     Progress: 76%
2025-09-12 19:10:57,895 MainProcess root INFO     Progress: 78%
2025-09-12 19:10:59,779 MainProcess root INFO     Progress: 79%
2025-09-12 19:11:01,675 MainProcess root INFO     Progress: 81%
2025-09-12 19:11:03,560 MainProcess root INFO     Progress: 82%
2025-09-12 19:11:05,469 MainProcess root INFO     Progress: 84%
2025-09-12 19:11:07,380 MainProcess root INFO     Progress: 85%
2025-09-12 19:11:09,255 MainProcess root INFO     Progress: 87%
2025-09-12 19:11:11,164 MainProcess root INFO     Progress: 89%
2025-09-12 19:11:13,054 MainProcess root INFO     Progress: 90%
2025-09-12 19:11:14,947 MainProcess root INFO     Progress: 92%
2025-09-12 19:11:16,832 MainProcess root INFO     Progress: 93%
2025-09-12 19:11:18,707 MainProcess root INFO     Progress: 95%
2025-09-12 19:11:20,602 MainProcess root INFO     Progress: 96%
2025-09-12 19:11:20,739 MainProcess root INFO     Finished deconvolution

## ROCm GPU acceleration

Speedup from ROCm over CPU version is 200x (1 minute runtime vs 200 minutes for CPU)

Test config:
CPU: AMD Ryzen 9 5950X 16-Core Processor
RAM: 32GB
GPU: AMD Navi 31 [Radeon RX 7900 XT/7900 XTX/7900 GRE/7900M] (rev ce)

no accel:

```
./benchmark.sh 
Running background extraction...
2025-09-09 14:03:51,577 MainProcess root INFO     Starting GraXpert CLI, Background-Extraction, version: 3.2.0a0.dev1 release: 1
2025-09-09 14:03:51,776 MainProcess root INFO     Using stored smoothing value 0.0.
2025-09-09 14:03:51,776 MainProcess root INFO     Using stored correction type Subtraction.
2025-09-09 14:03:51,776 MainProcess root INFO     Using user-supplied gpu acceleration setting False.
2025-09-09 14:03:52,276 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-09 14:03:52,276 MainProcess root INFO     Excecuting background extraction with the following parameters:
interpolation type - AI
         smoothing - 0.0
   correction type - Subtraction
     AI model path - /home/kevinh/.local/share/GraXpert/bge-ai-models/1.0.1/model.onnx
2025-09-09 14:03:53,054 MainProcess root INFO     Providers : ['CPUExecutionProvider']
2025-09-09 14:03:53,054 MainProcess root INFO     Used providers : ['CPUExecutionProvider']

real	0m6.212s
user	0m7.311s
sys	0m1.522s
Running deconvolution (object)...
2025-09-09 14:03:57,853 MainProcess root INFO     Starting GraXpert CLI, Deconvolution Obj, version: 3.2.0a0.dev1 release: 1
2025-09-09 14:03:57,920 MainProcess root INFO     Using stored deconvolution strength value 0.5.
2025-09-09 14:03:57,920 MainProcess root INFO     Using stored deconvolution psfsize value 5.0.
2025-09-09 14:03:57,920 MainProcess root INFO     Using stored batch size value 4.
2025-09-09 14:03:57,920 MainProcess root INFO     Using user-supplied gpu acceleration setting False.
2025-09-09 14:03:58,434 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-09 14:03:58,434 MainProcess root INFO     Excecuting deconvolution on objects with the following parameters:
AI model path - /home/kevinh/.local/share/GraXpert/deconvolution-object-ai-models/1.0.1/model.onnx
deconvolution strength - 0.5
deconvolution psfsize - 5.0
2025-09-09 14:03:58,435 MainProcess root INFO     Starting deconvolution
2025-09-09 14:03:58,435 MainProcess root INFO     Calculated normalized PSFsize value: 0.2951167728237792
2025-09-09 14:03:59,522 MainProcess root INFO     Available inference providers : ['CPUExecutionProvider']
2025-09-09 14:03:59,522 MainProcess root INFO     Used inference providers : ['CPUExecutionProvider']
2025-09-09 14:04:03,830 MainProcess root INFO     Progress: 1%
2025-09-09 14:04:05,728 MainProcess root INFO     Progress: 3%
2025-09-09 14:04:07,876 MainProcess root INFO     Progress: 4%
2025-09-09 14:04:09,768 MainProcess root INFO     Progress: 6%
2025-09-09 14:04:11,807 MainProcess root INFO     Progress: 7%
2025-09-09 14:04:13,725 MainProcess root INFO     Progress: 9%
2025-09-09 14:04:15,614 MainProcess root INFO     Progress: 10%
2025-09-09 14:04:17,494 MainProcess root INFO     Progress: 12%
2025-09-09 14:04:19,404 MainProcess root INFO     Progress: 14%
2025-09-09 14:04:21,297 MainProcess root INFO     Progress: 15%
2025-09-09 14:04:23,521 MainProcess root INFO     Progress: 17%
2025-09-09 14:04:25,403 MainProcess root INFO     Progress: 18%
2025-09-09 14:04:27,282 MainProcess root INFO     Progress: 20%
2025-09-09 14:04:29,175 MainProcess root INFO     Progress: 21%
2025-09-09 14:04:31,124 MainProcess root INFO     Progress: 23%
2025-09-09 14:04:33,367 MainProcess root INFO     Progress: 25%
2025-09-09 14:04:35,641 MainProcess root INFO     Progress: 26%
2025-09-09 14:04:37,916 MainProcess root INFO     Progress: 28%
2025-09-09 14:04:40,156 MainProcess root INFO     Progress: 29%
2025-09-09 14:04:42,078 MainProcess root INFO     Progress: 31%
2025-09-09 14:04:44,256 MainProcess root INFO     Progress: 32%
2025-09-09 14:04:46,133 MainProcess root INFO     Progress: 34%
2025-09-09 14:04:48,034 MainProcess root INFO     Progress: 35%
2025-09-09 14:04:50,288 MainProcess root INFO     Progress: 37%
2025-09-09 14:04:52,494 MainProcess root INFO     Progress: 39%
2025-09-09 14:04:54,411 MainProcess root INFO     Progress: 40%
2025-09-09 14:04:56,377 MainProcess root INFO     Progress: 42%
2025-09-09 14:04:58,325 MainProcess root INFO     Progress: 43%
2025-09-09 14:05:00,182 MainProcess root INFO     Progress: 45%
2025-09-09 14:05:02,104 MainProcess root INFO     Progress: 46%
2025-09-09 14:05:03,994 MainProcess root INFO     Progress: 48%
2025-09-09 14:05:05,891 MainProcess root INFO     Progress: 50%
2025-09-09 14:05:07,794 MainProcess root INFO     Progress: 51%
2025-09-09 14:05:09,664 MainProcess root INFO     Progress: 53%
2025-09-09 14:05:11,912 MainProcess root INFO     Progress: 54%
2025-09-09 14:05:14,159 MainProcess root INFO     Progress: 56%
2025-09-09 14:05:16,014 MainProcess root INFO     Progress: 57%
2025-09-09 14:05:18,254 MainProcess root INFO     Progress: 59%
2025-09-09 14:05:20,184 MainProcess root INFO     Progress: 60%
2025-09-09 14:05:22,097 MainProcess root INFO     Progress: 62%
2025-09-09 14:05:24,037 MainProcess root INFO     Progress: 64%
2025-09-09 14:05:25,924 MainProcess root INFO     Progress: 65%
2025-09-09 14:05:27,844 MainProcess root INFO     Progress: 67%
2025-09-09 14:05:29,752 MainProcess root INFO     Progress: 68%
2025-09-09 14:05:31,632 MainProcess root INFO     Progress: 70%
2025-09-09 14:05:33,534 MainProcess root INFO     Progress: 71%
2025-09-09 14:05:35,742 MainProcess root INFO     Progress: 73%
2025-09-09 14:05:37,636 MainProcess root INFO     Progress: 75%
2025-09-09 14:05:39,572 MainProcess root INFO     Progress: 76%
2025-09-09 14:05:41,880 MainProcess root INFO     Progress: 78%
2025-09-09 14:05:43,841 MainProcess root INFO     Progress: 79%
2025-09-09 14:05:46,176 MainProcess root INFO     Progress: 81%
2025-09-09 14:05:48,462 MainProcess root INFO     Progress: 82%
2025-09-09 14:05:50,393 MainProcess root INFO     Progress: 84%
2025-09-09 14:05:52,719 MainProcess root INFO     Progress: 85%
2025-09-09 14:05:55,046 MainProcess root INFO     Progress: 87%
2025-09-09 14:05:57,288 MainProcess root INFO     Progress: 89%
2025-09-09 14:05:59,222 MainProcess root INFO     Progress: 90%
2025-09-09 14:06:01,152 MainProcess root INFO     Progress: 92%
2025-09-09 14:06:03,193 MainProcess root INFO     Progress: 93%
2025-09-09 14:06:05,126 MainProcess root INFO     Progress: 95%
2025-09-09 14:06:07,165 MainProcess root INFO     Progress: 96%
2025-09-09 14:06:07,395 MainProcess root INFO     Finished deconvolution

real	2m14.264s
user	30m32.652s
sys	0m3.930s
Running denoising...
2025-09-09 14:06:12,042 MainProcess root INFO     Starting GraXpert CLI, Denoising, version: 3.2.0a0.dev1 release: 1
2025-09-09 14:06:12,112 MainProcess root INFO     Using stored denoise strength value 0.5.
2025-09-09 14:06:12,112 MainProcess root INFO     Using stored batch size value 4.
2025-09-09 14:06:12,112 MainProcess root INFO     Using user-supplied gpu acceleration setting False.
2025-09-09 14:06:13,284 MainProcess root INFO     Using AI version 3.0.2. You can overwrite this by providing the argument '-ai_version'
2025-09-09 14:06:13,284 MainProcess root INFO     Excecuting denoising with the following parameters:
AI model path - /home/kevinh/.local/share/GraXpert/denoise-ai-models/3.0.2/model.onnx
denoise strength - 0.5
2025-09-09 14:06:13,284 MainProcess root INFO     Starting denoising
2025-09-09 14:06:15,467 MainProcess root INFO     Available inference providers : ['CPUExecutionProvider']
2025-09-09 14:06:15,468 MainProcess root INFO     Used inference providers : ['CPUExecutionProvider']
2025-09-09 14:06:28,460 MainProcess root INFO     Progress: 1%
2025-09-09 14:06:37,305 MainProcess root INFO     Progress: 2%
2025-09-09 14:06:46,056 MainProcess root INFO     Progress: 3%
2025-09-09 14:06:54,525 MainProcess root INFO     Progress: 4%
2025-09-09 14:07:02,886 MainProcess root INFO     Progress: 5%
2025-09-09 14:07:07,070 MainProcess root INFO     Progress: 6%
2025-09-09 14:07:15,653 MainProcess root INFO     Progress: 7%
2025-09-09 14:07:24,144 MainProcess root INFO     Progress: 8%
2025-09-09 14:07:32,711 MainProcess root INFO     Progress: 9%
2025-09-09 14:07:41,068 MainProcess root INFO     Progress: 10%
2025-09-09 14:07:49,327 MainProcess root INFO     Progress: 11%
2025-09-09 14:07:53,434 MainProcess root INFO     Progress: 12%
2025-09-09 14:08:01,717 MainProcess root INFO     Progress: 13%
2025-09-09 14:08:09,980 MainProcess root INFO     Progress: 14%
2025-09-09 14:08:18,256 MainProcess root INFO     Progress: 15%
2025-09-09 14:08:26,527 MainProcess root INFO     Progress: 16%
2025-09-09 14:08:30,647 MainProcess root INFO     Progress: 17%
2025-09-09 14:08:39,276 MainProcess root INFO     Progress: 18%
2025-09-09 14:08:47,729 MainProcess root INFO     Progress: 19%
2025-09-09 14:08:56,315 MainProcess root INFO     Progress: 20%
2025-09-09 14:09:05,329 MainProcess root INFO     Progress: 21%
2025-09-09 14:09:14,399 MainProcess root INFO     Progress: 22%
2025-09-09 14:09:19,239 MainProcess root INFO     Progress: 23%
2025-09-09 14:09:28,162 MainProcess root INFO     Progress: 24%
2025-09-09 14:09:36,474 MainProcess root INFO     Progress: 25%
2025-09-09 14:09:44,735 MainProcess root INFO     Progress: 26%
2025-09-09 14:09:53,229 MainProcess root INFO     Progress: 27%
2025-09-09 14:10:01,490 MainProcess root INFO     Progress: 28%
2025-09-09 14:10:05,776 MainProcess root INFO     Progress: 29%
2025-09-09 14:10:13,992 MainProcess root INFO     Progress: 30%
2025-09-09 14:10:22,270 MainProcess root INFO     Progress: 31%
2025-09-09 14:10:30,568 MainProcess root INFO     Progress: 32%
2025-09-09 14:10:39,162 MainProcess root INFO     Progress: 33%
2025-09-09 14:10:43,321 MainProcess root INFO     Progress: 34%
2025-09-09 14:10:51,590 MainProcess root INFO     Progress: 35%
2025-09-09 14:10:59,982 MainProcess root INFO     Progress: 36%
2025-09-09 14:11:08,435 MainProcess root INFO     Progress: 37%
2025-09-09 14:11:16,731 MainProcess root INFO     Progress: 38%
2025-09-09 14:11:25,346 MainProcess root INFO     Progress: 39%
2025-09-09 14:11:29,908 MainProcess root INFO     Progress: 40%
2025-09-09 14:11:38,430 MainProcess root INFO     Progress: 41%
2025-09-09 14:11:46,745 MainProcess root INFO     Progress: 42%
2025-09-09 14:11:55,032 MainProcess root INFO     Progress: 43%
2025-09-09 14:12:03,527 MainProcess root INFO     Progress: 44%
2025-09-09 14:12:12,109 MainProcess root INFO     Progress: 45%
2025-09-09 14:12:16,269 MainProcess root INFO     Progress: 46%
2025-09-09 14:12:24,958 MainProcess root INFO     Progress: 47%
2025-09-09 14:12:33,501 MainProcess root INFO     Progress: 48%
2025-09-09 14:12:42,095 MainProcess root INFO     Progress: 49%
2025-09-09 14:12:50,511 MainProcess root INFO     Progress: 50%
2025-09-09 14:12:54,749 MainProcess root INFO     Progress: 51%
2025-09-09 14:13:03,197 MainProcess root INFO     Progress: 52%
2025-09-09 14:13:11,784 MainProcess root INFO     Progress: 53%
2025-09-09 14:13:20,231 MainProcess root INFO     Progress: 54%
2025-09-09 14:13:28,900 MainProcess root INFO     Progress: 55%
2025-09-09 14:13:37,305 MainProcess root INFO     Progress: 56%
2025-09-09 14:13:41,434 MainProcess root INFO     Progress: 57%
2025-09-09 14:13:50,009 MainProcess root INFO     Progress: 58%
2025-09-09 14:13:58,690 MainProcess root INFO     Progress: 59%
2025-09-09 14:14:07,168 MainProcess root INFO     Progress: 60%
2025-09-09 14:14:15,554 MainProcess root INFO     Progress: 61%
2025-09-09 14:14:19,735 MainProcess root INFO     Progress: 62%
2025-09-09 14:14:28,079 MainProcess root INFO     Progress: 63%
2025-09-09 14:14:36,887 MainProcess root INFO     Progress: 64%
2025-09-09 14:14:45,298 MainProcess root INFO     Progress: 65%
2025-09-09 14:14:54,314 MainProcess root INFO     Progress: 66%
2025-09-09 14:15:03,154 MainProcess root INFO     Progress: 67%
2025-09-09 14:15:07,550 MainProcess root INFO     Progress: 68%
2025-09-09 14:15:15,878 MainProcess root INFO     Progress: 69%
2025-09-09 14:15:24,478 MainProcess root INFO     Progress: 70%
2025-09-09 14:15:32,725 MainProcess root INFO     Progress: 71%
2025-09-09 14:15:41,126 MainProcess root INFO     Progress: 72%
2025-09-09 14:15:49,426 MainProcess root INFO     Progress: 73%
2025-09-09 14:15:53,757 MainProcess root INFO     Progress: 74%
2025-09-09 14:16:02,317 MainProcess root INFO     Progress: 75%
2025-09-09 14:16:10,898 MainProcess root INFO     Progress: 76%
2025-09-09 14:16:19,318 MainProcess root INFO     Progress: 77%
2025-09-09 14:16:28,244 MainProcess root INFO     Progress: 78%
2025-09-09 14:16:32,367 MainProcess root INFO     Progress: 79%
2025-09-09 14:16:40,638 MainProcess root INFO     Progress: 80%
2025-09-09 14:16:49,054 MainProcess root INFO     Progress: 81%
2025-09-09 14:16:57,619 MainProcess root INFO     Progress: 82%
2025-09-09 14:17:06,094 MainProcess root INFO     Progress: 83%
2025-09-09 14:17:14,330 MainProcess root INFO     Progress: 84%
2025-09-09 14:17:18,493 MainProcess root INFO     Progress: 85%
2025-09-09 14:17:26,753 MainProcess root INFO     Progress: 86%
2025-09-09 14:17:35,069 MainProcess root INFO     Progress: 87%
2025-09-09 14:17:43,454 MainProcess root INFO     Progress: 88%
2025-09-09 14:17:51,729 MainProcess root INFO     Progress: 89%
2025-09-09 14:18:00,117 MainProcess root INFO     Progress: 90%
2025-09-09 14:18:04,340 MainProcess root INFO     Progress: 91%
2025-09-09 14:18:12,604 MainProcess root INFO     Progress: 92%
2025-09-09 14:18:20,868 MainProcess root INFO     Progress: 93%
2025-09-09 14:18:29,577 MainProcess root INFO     Progress: 94%
2025-09-09 14:18:38,170 MainProcess root INFO     Progress: 95%
2025-09-09 14:18:42,307 MainProcess root INFO     Progress: 96%
2025-09-09 14:18:50,742 MainProcess root INFO     Progress: 97%
2025-09-09 14:18:59,114 MainProcess root INFO     Progress: 98%
2025-09-09 14:19:04,234 MainProcess root INFO     Progress: 99%
2025-09-09 14:19:04,878 MainProcess root INFO     Finished denoising

real	12m57.519s
user	200m1.987s
sys	0m6.569s
```

Now with GPU acceleration on

```
vscode ➜ /workspaces/graxpert (pr-fixrocm) $ ./benchmark.sh 
Running background extraction...
2025-09-11 21:29:44,583 MainProcess root INFO     Starting GraXpert CLI, Background-Extraction, version: 3.2.0a0.dev1 release: 1
2025-09-11 21:29:44,755 MainProcess root INFO     Using stored smoothing value 0.0.
2025-09-11 21:29:44,755 MainProcess root INFO     Using stored correction type Subtraction.
2025-09-11 21:29:44,755 MainProcess root INFO     Using user-supplied gpu acceleration setting True.
2025-09-11 21:29:45,257 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-11 21:29:45,258 MainProcess root INFO     Excecuting background extraction with the following parameters:
interpolation type - AI
         smoothing - 0.0
   correction type - Subtraction
     AI model path - /home/vscode/.local/share/GraXpert/bge-ai-models/1.0.1/model.onnx
2025-09-11 21:29:50,803 MainProcess root INFO     Providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-09-11 21:29:50,803 MainProcess root INFO     Used providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']

real    0m11.455s
user    0m9.134s
sys     0m4.199s
Running deconvolution (object)...
2025-09-11 21:29:56,087 MainProcess root INFO     Starting GraXpert CLI, Deconvolution Obj, version: 3.2.0a0.dev1 release: 1
2025-09-11 21:29:56,142 MainProcess root INFO     Using stored deconvolution strength value 0.5.
2025-09-11 21:29:56,143 MainProcess root INFO     Using stored deconvolution psfsize value 5.0.
2025-09-11 21:29:56,143 MainProcess root INFO     Using stored batch size value 4.
2025-09-11 21:29:56,143 MainProcess root INFO     Using user-supplied gpu acceleration setting True.
2025-09-11 21:29:56,646 MainProcess root INFO     Using AI version 1.0.1. You can overwrite this by providing the argument '-ai_version'
2025-09-11 21:29:56,646 MainProcess root INFO     Excecuting deconvolution on objects with the following parameters:
AI model path - /home/vscode/.local/share/GraXpert/deconvolution-object-ai-models/1.0.1/model.onnx
deconvolution strength - 0.5
deconvolution psfsize - 5.0
2025-09-11 21:29:56,646 MainProcess root INFO     Starting deconvolution
2025-09-11 21:29:56,646 MainProcess root INFO     Calculated normalized PSFsize value: 0.2951167728237792
2025-09-11 21:30:02,462 MainProcess root INFO     Available inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-09-11 21:30:02,462 MainProcess root INFO     Used inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 67108864, provided ptr: 0x7f88b2400400 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 67108864, provided ptr: 0x7f88b2400400 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 134217728, provided ptr: 0x7f88adc00000 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 134217728, provided ptr: 0x7f88adc00000 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 268435456, provided ptr: 0x7f88ffe00000 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 268435456, provided ptr: 0x7f88ffe00000 size: 33554432
2025-09-11 21:31:02,677 MainProcess root INFO     Progress: 1%
2025-09-11 21:31:02,731 MainProcess root INFO     Progress: 3%
2025-09-11 21:31:02,785 MainProcess root INFO     Progress: 4%
2025-09-11 21:31:02,840 MainProcess root INFO     Progress: 6%
2025-09-11 21:31:02,895 MainProcess root INFO     Progress: 7%
2025-09-11 21:31:02,949 MainProcess root INFO     Progress: 9%
2025-09-11 21:31:03,004 MainProcess root INFO     Progress: 10%
2025-09-11 21:31:03,059 MainProcess root INFO     Progress: 12%
2025-09-11 21:31:03,115 MainProcess root INFO     Progress: 14%
2025-09-11 21:31:03,170 MainProcess root INFO     Progress: 15%
2025-09-11 21:31:03,226 MainProcess root INFO     Progress: 17%
2025-09-11 21:31:03,282 MainProcess root INFO     Progress: 18%
2025-09-11 21:31:03,337 MainProcess root INFO     Progress: 20%
2025-09-11 21:31:03,392 MainProcess root INFO     Progress: 21%
2025-09-11 21:31:03,448 MainProcess root INFO     Progress: 23%
2025-09-11 21:31:03,503 MainProcess root INFO     Progress: 25%
2025-09-11 21:31:03,559 MainProcess root INFO     Progress: 26%
2025-09-11 21:31:03,613 MainProcess root INFO     Progress: 28%
2025-09-11 21:31:03,669 MainProcess root INFO     Progress: 29%
2025-09-11 21:31:03,724 MainProcess root INFO     Progress: 31%
2025-09-11 21:31:03,779 MainProcess root INFO     Progress: 32%
2025-09-11 21:31:03,834 MainProcess root INFO     Progress: 34%
2025-09-11 21:31:03,889 MainProcess root INFO     Progress: 35%
2025-09-11 21:31:03,945 MainProcess root INFO     Progress: 37%
2025-09-11 21:31:04,002 MainProcess root INFO     Progress: 39%
2025-09-11 21:31:04,057 MainProcess root INFO     Progress: 40%
2025-09-11 21:31:04,113 MainProcess root INFO     Progress: 42%
2025-09-11 21:31:04,168 MainProcess root INFO     Progress: 43%
2025-09-11 21:31:04,223 MainProcess root INFO     Progress: 45%
2025-09-11 21:31:04,279 MainProcess root INFO     Progress: 46%
2025-09-11 21:31:04,334 MainProcess root INFO     Progress: 48%
2025-09-11 21:31:04,389 MainProcess root INFO     Progress: 50%
2025-09-11 21:31:04,443 MainProcess root INFO     Progress: 51%
2025-09-11 21:31:04,498 MainProcess root INFO     Progress: 53%
2025-09-11 21:31:04,553 MainProcess root INFO     Progress: 54%
2025-09-11 21:31:04,608 MainProcess root INFO     Progress: 56%
2025-09-11 21:31:04,664 MainProcess root INFO     Progress: 57%
2025-09-11 21:31:04,719 MainProcess root INFO     Progress: 59%
2025-09-11 21:31:04,775 MainProcess root INFO     Progress: 60%
2025-09-11 21:31:04,830 MainProcess root INFO     Progress: 62%
2025-09-11 21:31:04,886 MainProcess root INFO     Progress: 64%
2025-09-11 21:31:04,941 MainProcess root INFO     Progress: 65%
2025-09-11 21:31:04,996 MainProcess root INFO     Progress: 67%
2025-09-11 21:31:05,050 MainProcess root INFO     Progress: 68%
2025-09-11 21:31:05,105 MainProcess root INFO     Progress: 70%
2025-09-11 21:31:05,160 MainProcess root INFO     Progress: 71%
2025-09-11 21:31:05,216 MainProcess root INFO     Progress: 73%
2025-09-11 21:31:05,270 MainProcess root INFO     Progress: 75%
2025-09-11 21:31:05,326 MainProcess root INFO     Progress: 76%
2025-09-11 21:31:05,380 MainProcess root INFO     Progress: 78%
2025-09-11 21:31:05,435 MainProcess root INFO     Progress: 79%
2025-09-11 21:31:05,491 MainProcess root INFO     Progress: 81%
2025-09-11 21:31:05,546 MainProcess root INFO     Progress: 82%
2025-09-11 21:31:05,601 MainProcess root INFO     Progress: 84%
2025-09-11 21:31:05,656 MainProcess root INFO     Progress: 85%
2025-09-11 21:31:05,710 MainProcess root INFO     Progress: 87%
2025-09-11 21:31:05,765 MainProcess root INFO     Progress: 89%
2025-09-11 21:31:05,819 MainProcess root INFO     Progress: 90%
2025-09-11 21:31:05,875 MainProcess root INFO     Progress: 92%
2025-09-11 21:31:05,929 MainProcess root INFO     Progress: 93%
2025-09-11 21:31:05,984 MainProcess root INFO     Progress: 95%
2025-09-11 21:31:06,039 MainProcess root INFO     Progress: 96%
2025-09-11 21:31:06,061 MainProcess root INFO     Finished deconvolution

real    1m14.990s
user    1m11.330s
sys     0m3.828s
Running denoising...
2025-09-11 21:31:11,059 MainProcess root INFO     Starting GraXpert CLI, Denoising, version: 3.2.0a0.dev1 release: 1
2025-09-11 21:31:11,114 MainProcess root INFO     Using stored denoise strength value 0.5.
2025-09-11 21:31:11,114 MainProcess root INFO     Using stored batch size value 4.
2025-09-11 21:31:11,114 MainProcess root INFO     Using user-supplied gpu acceleration setting True.
2025-09-11 21:31:12,294 MainProcess root INFO     Using AI version 3.0.2. You can overwrite this by providing the argument '-ai_version'
2025-09-11 21:31:12,294 MainProcess root INFO     Excecuting denoising with the following parameters:
AI model path - /home/vscode/.local/share/GraXpert/denoise-ai-models/3.0.2/model.onnx
denoise strength - 0.5
2025-09-11 21:31:12,294 MainProcess root INFO     Starting denoising
2025-09-11 21:31:18,997 MainProcess root INFO     Available inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-09-11 21:31:18,997 MainProcess root INFO     Used inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-09-11 21:31:40,815 MainProcess root INFO     Progress: 1%
2025-09-11 21:31:41,187 MainProcess root INFO     Progress: 2%
2025-09-11 21:31:41,558 MainProcess root INFO     Progress: 3%
2025-09-11 21:31:41,921 MainProcess root INFO     Progress: 4%
2025-09-11 21:31:42,294 MainProcess root INFO     Progress: 5%
2025-09-11 21:31:42,476 MainProcess root INFO     Progress: 6%
2025-09-11 21:31:42,847 MainProcess root INFO     Progress: 7%
2025-09-11 21:31:43,219 MainProcess root INFO     Progress: 8%
2025-09-11 21:31:43,593 MainProcess root INFO     Progress: 9%
2025-09-11 21:31:43,964 MainProcess root INFO     Progress: 10%
2025-09-11 21:31:44,327 MainProcess root INFO     Progress: 11%
2025-09-11 21:31:44,510 MainProcess root INFO     Progress: 12%
2025-09-11 21:31:44,884 MainProcess root INFO     Progress: 13%
2025-09-11 21:31:45,256 MainProcess root INFO     Progress: 14%
2025-09-11 21:31:45,621 MainProcess root INFO     Progress: 15%
2025-09-11 21:31:45,994 MainProcess root INFO     Progress: 16%
2025-09-11 21:31:46,176 MainProcess root INFO     Progress: 17%
2025-09-11 21:31:46,551 MainProcess root INFO     Progress: 18%
2025-09-11 21:31:46,925 MainProcess root INFO     Progress: 19%
2025-09-11 21:31:47,290 MainProcess root INFO     Progress: 20%
2025-09-11 21:31:47,665 MainProcess root INFO     Progress: 21%
2025-09-11 21:31:48,040 MainProcess root INFO     Progress: 22%
2025-09-11 21:31:48,223 MainProcess root INFO     Progress: 23%
2025-09-11 21:31:48,597 MainProcess root INFO     Progress: 24%
2025-09-11 21:31:48,962 MainProcess root INFO     Progress: 25%
2025-09-11 21:31:49,336 MainProcess root INFO     Progress: 26%
2025-09-11 21:31:49,710 MainProcess root INFO     Progress: 27%
2025-09-11 21:31:50,084 MainProcess root INFO     Progress: 28%
2025-09-11 21:31:50,267 MainProcess root INFO     Progress: 29%
2025-09-11 21:31:50,642 MainProcess root INFO     Progress: 30%
2025-09-11 21:31:51,067 MainProcess root INFO     Progress: 31%
2025-09-11 21:31:51,441 MainProcess root INFO     Progress: 32%
2025-09-11 21:31:51,815 MainProcess root INFO     Progress: 33%
2025-09-11 21:31:51,997 MainProcess root INFO     Progress: 34%
2025-09-11 21:31:52,372 MainProcess root INFO     Progress: 35%
2025-09-11 21:31:52,747 MainProcess root INFO     Progress: 36%
2025-09-11 21:31:53,121 MainProcess root INFO     Progress: 37%
2025-09-11 21:31:53,495 MainProcess root INFO     Progress: 38%
2025-09-11 21:31:53,870 MainProcess root INFO     Progress: 39%
2025-09-11 21:31:54,053 MainProcess root INFO     Progress: 40%
2025-09-11 21:31:54,427 MainProcess root INFO     Progress: 41%
2025-09-11 21:31:54,802 MainProcess root INFO     Progress: 42%
2025-09-11 21:31:55,176 MainProcess root INFO     Progress: 43%
2025-09-11 21:31:55,551 MainProcess root INFO     Progress: 44%
2025-09-11 21:31:55,927 MainProcess root INFO     Progress: 45%
2025-09-11 21:31:56,110 MainProcess root INFO     Progress: 46%
2025-09-11 21:31:56,475 MainProcess root INFO     Progress: 47%
2025-09-11 21:31:56,842 MainProcess root INFO     Progress: 48%
2025-09-11 21:31:57,217 MainProcess root INFO     Progress: 49%
2025-09-11 21:31:57,593 MainProcess root INFO     Progress: 50%
2025-09-11 21:31:57,776 MainProcess root INFO     Progress: 51%
2025-09-11 21:31:58,150 MainProcess root INFO     Progress: 52%
2025-09-11 21:31:58,525 MainProcess root INFO     Progress: 53%
2025-09-11 21:31:58,900 MainProcess root INFO     Progress: 54%
2025-09-11 21:31:59,276 MainProcess root INFO     Progress: 55%
2025-09-11 21:31:59,651 MainProcess root INFO     Progress: 56%
2025-09-11 21:31:59,834 MainProcess root INFO     Progress: 57%
2025-09-11 21:32:00,210 MainProcess root INFO     Progress: 58%
2025-09-11 21:32:00,585 MainProcess root INFO     Progress: 59%
2025-09-11 21:32:00,952 MainProcess root INFO     Progress: 60%
2025-09-11 21:32:01,326 MainProcess root INFO     Progress: 61%
2025-09-11 21:32:01,509 MainProcess root INFO     Progress: 62%
2025-09-11 21:32:01,876 MainProcess root INFO     Progress: 63%
2025-09-11 21:32:02,250 MainProcess root INFO     Progress: 64%
2025-09-11 21:32:02,624 MainProcess root INFO     Progress: 65%
2025-09-11 21:32:02,999 MainProcess root INFO     Progress: 66%
2025-09-11 21:32:03,366 MainProcess root INFO     Progress: 67%
2025-09-11 21:32:03,549 MainProcess root INFO     Progress: 68%
2025-09-11 21:32:03,924 MainProcess root INFO     Progress: 69%
2025-09-11 21:32:04,290 MainProcess root INFO     Progress: 70%
2025-09-11 21:32:04,665 MainProcess root INFO     Progress: 71%
2025-09-11 21:32:05,032 MainProcess root INFO     Progress: 72%
2025-09-11 21:32:05,408 MainProcess root INFO     Progress: 73%
2025-09-11 21:32:05,595 MainProcess root INFO     Progress: 74%
2025-09-11 21:32:05,968 MainProcess root INFO     Progress: 75%
2025-09-11 21:32:06,390 MainProcess root INFO     Progress: 76%
2025-09-11 21:32:06,762 MainProcess root INFO     Progress: 77%
2025-09-11 21:32:07,129 MainProcess root INFO     Progress: 78%
2025-09-11 21:32:07,317 MainProcess root INFO     Progress: 79%
2025-09-11 21:32:07,692 MainProcess root INFO     Progress: 80%
2025-09-11 21:32:08,067 MainProcess root INFO     Progress: 81%
2025-09-11 21:32:08,432 MainProcess root INFO     Progress: 82%
2025-09-11 21:32:08,799 MainProcess root INFO     Progress: 83%
2025-09-11 21:32:09,168 MainProcess root INFO     Progress: 84%
2025-09-11 21:32:09,352 MainProcess root INFO     Progress: 85%
2025-09-11 21:32:09,718 MainProcess root INFO     Progress: 86%
2025-09-11 21:32:10,085 MainProcess root INFO     Progress: 87%
2025-09-11 21:32:10,458 MainProcess root INFO     Progress: 88%
2025-09-11 21:32:10,831 MainProcess root INFO     Progress: 89%
2025-09-11 21:32:11,198 MainProcess root INFO     Progress: 90%
2025-09-11 21:32:11,381 MainProcess root INFO     Progress: 91%
2025-09-11 21:32:11,747 MainProcess root INFO     Progress: 92%
2025-09-11 21:32:12,122 MainProcess root INFO     Progress: 93%
2025-09-11 21:32:12,494 MainProcess root INFO     Progress: 94%
2025-09-11 21:32:12,857 MainProcess root INFO     Progress: 95%
2025-09-11 21:32:13,039 MainProcess root INFO     Progress: 96%
2025-09-11 21:32:13,404 MainProcess root INFO     Progress: 97%
2025-09-11 21:32:13,768 MainProcess root INFO     Progress: 98%
2025-09-11 21:32:26,649 MainProcess root INFO     Progress: 99%
2025-09-11 21:32:27,322 MainProcess root INFO     Finished denoising

real    1m21.368s
user    1m20.913s
sys     0m21.855s
```