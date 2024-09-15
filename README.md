# Data Compression is not enough

Content Size: 19.1mb

| Optimization Techniques             | Size   | Change   |
| ----------------------------------- | ------ | -------- |
| Compact                             | 17.4mb | -1.7mb   |
| Compact + Lean                      | 11.9mb | -7.2mb   |
| Compact + Lean + Normalize          | 5.5mb  | -13.6mb  |
| Compact + Lean + Normalize + Gzip   | 429kb  | -18.7mb  |
| Compact + Lean + Normalize + Brotli | 70.5kb | -19.03mb |

| Data Compression | Size   | Change   |
| ---------------- | ------ | -------- |
| Gzip             | 705kb  | -18.4mb  |
| Brotli           | 90.2kb | -19.01mb |

| Optimization Techniques and Data Compression | Size   | Change   |
| -------------------------------------------- | ------ | -------- |
| Compact + Lean + Normalize + Brotli          | 70.5kb | -19.03mb |
| Brotli                                       | 90.2kb | -19.01mb |
| Compact + Lean + Normalize + Gzip            | 429kb  | -18.7mb  |
| Gzip                                         | 705kb  | -18.4mb  |
| Compact + Lean + Normalize                   | 5.5mb  | -13.6mb  |
| Compact + Lean                               | 11.9mb | -7.2mb   |
| Compact                                      | 17.4mb | -1.7mb   |
