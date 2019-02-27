# jianhua python
#### This is a repository for my python scripts
## liftover
convert Genome Build of txt or csv file using [pyliftover](https://pypi.org/project/pyliftover/)
#### Requiment
- python3 (conda)
- pyliftover
#### Install pyliftover
```
pip install pyliftover
```
you may need install `msgpack` using `pip install msgpack` for dependcy
### Usage
```
python liftover.py -c 0 -p 1 test.txt test_lifted.txt
```
```
Original Build: hg19	New Build: hg38	Thread: 20

Successful converted: 865,762    Failed: 97
Writing result to test4_lifted.txt...
Complete 100.00%

total: 865,859	succeeded: 865,762	failed: 97	in: 11.89s.
Have a nice day! :)
```
### Help
```
positional arguments:
  input           input unlifted file
  output          output lifted file

optional arguments:
  -h, --help      show this help message and exit
  -c , --chr      colunm positon of chromosome (0-based), default=0
  -p , --pos      colunm positon of base pair (0-based), default=1
  -o , --old      Genome Build of input file, choose from
                  [hg17,hg18,hg19,hg38], default=hg19
  -n , --new      Genome Build of output file, choose from
                  [hg17,hg18,hg19,hg38], default=hg38
  -s , --sep      separator of input file, choose from [table,comma],
                  default=table
  -t , --thread   threads you want to run, default=20
  --withchr       exist when chromosome of input starts with chr, and output
                  starts with chr, either
  --gzip          exist when input is .gz file, and output .gz file, either
  --headless      exist when input is headless file, and output headless file,
                  either
```
