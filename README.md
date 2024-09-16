# Data Compression is not enough

| Optimizations                       | Size   | Change   | Time (Slow 4g) | Time (3G) |
| ----------------------------------- | ------ | -------- | -------------- | --------- |
| No optimizations                    | 19.1mb | -0.00mb  |                |           |
| Compact                             | 14.7mb | -1.70mb  |                |           |
| Compact + Lean                      | 11.9mb | -7.20mb  |                |           |
| Compact + Lean + Normalize          | 5.1mb  | -14.00mb | ~29sec         | ~1.7min   |
| Compact + Lean + Normalize + Gzip   | 429kb  | -18.67mb | ~3sec          | ~11sec    |
| Compact + Lean + Normalize + Brotli | 70.5kb | -19.03mb | ~1sec          | ~3sec     |
| Gzip                                | 705kb  | -18.04mb | ~13sec         | ~16sec    |
| Brotli                              | 90.2kb | -19.01mb | ~3sec          | ~4sec     |
