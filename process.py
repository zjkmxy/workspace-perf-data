import re
import os

RTT_STD = [
  [10, 121, 255, 115],
  [121, 116, 247, 141],
  [255, 247, 250, 218],
  [115, 141, 218, 110],
]

FREQS = [50, 100, 500, 1000]
NODE_CNTS = [1, 2, 3, 4]


def normed(number: int, recver: int, sender: int) -> float:
  return number / RTT_STD[recver-1][(sender-1)%5] * 100


def process_line(line: str, recver: int) -> str:
  match = re.match('node-([0-9]+)-[0-9]+,([0-9]+),([0-9]+)', line)
  if match is None:
    return ''
  sender = int(match.group(1))
  seq = int(match.group(2))
  latency = int(match.group(3))
  new_val = normed(latency, recver, sender)
  if recver == 1 and sender % 5 == 1:
    return ''  # Remove not accurate SUNS-SUNS data
  return f'{sender},{seq},{new_val}'


def filter_one_hop(line: str, recver: int) -> str:
  match = re.match('node-([0-9]+)-[0-9]+,([0-9]+),([0-9]+)', line)
  if match is None:
    return ''
  sender = int(match.group(1))
  seq = int(match.group(2))
  latency = int(match.group(3))
  if recver == (sender % 5):
    return ''  # Remove one hop data
  return f'{sender},{seq},{latency}'


def process_file(freq: int, node_cnt: int):
  for recver in range(1, 5):
    with open(f'./logs/udp/{node_cnt}-{freq}/{recver}.csv', 'r') as f_in:
      os.makedirs(f'./logs/processed/{node_cnt}-{freq}', exist_ok=True)
      first_line = True
      with open(f'./logs/processed/{node_cnt}-{freq}/{recver}.csv', 'w') as f_out:
        for line in f_in:
          if first_line:
            first_line = False
            print('id,seq,delay', file=f_out)
          else:
            new_line = process_line(line, recver)
            if new_line:
              print(new_line, file=f_out)


def filter_self(freq: int, node_cnt: int):
  for recver in range(1, 5):
    with open(f'./logs/udp/{node_cnt}-{freq}/{recver}.csv', 'r') as f_in:
      os.makedirs(f'./logs/udp_filtered/{node_cnt}-{freq}', exist_ok=True)
      first_line = True
      with open(f'./logs/udp_filtered/{node_cnt}-{freq}/{recver}.csv', 'w') as f_out:
        for line in f_in:
          if first_line:
            first_line = False
            print('id,seq,delay', file=f_out)
          else:
            new_line = filter_one_hop(line, recver)
            if new_line:
              print(new_line, file=f_out)


def main():
  for node_cnt in NODE_CNTS:
    for freq in FREQS:
      filter_self(freq, node_cnt)


if __name__ == '__main__':
  main()
