#!/usr/bin/env python3
# Copyright 2019 Marc-Antoine Ruel. All Rights Reserved. Use of this
# source code is governed by a BSD-style license that can be found in the
# LICENSE file.

"""Processes Banque Nationale Courtage Direct CSV export.

To generate the CSV:
 - https://client.bnc.ca/cdbn/history
 - Prendre les options par défaut.
"""

import argparse
import csv
import sys


def get_log(name):
  """Prend un export des activités de Banque Nationale Courtage Direct et
  retoune un dict.
  """
  comptes = {}
  with open(name, encoding='latin-1') as f:
    reader = csv.DictReader(f, strict=True)
    try:
      for row in reader:
        #print(row['Numéro de compte'])
        if row['Opération'] in ('Dividende', 'Intérêt', 'Distribution'):
          desc = row['Description du compte']
          sym = row['Symbole']
          if not sym:
            sym = 'compte'
          # Remet la date en ordre.
          date = row['Date du règlement'].split('/', 2)
          date = '%s/%s/%s' % (date[2], date[1], date[0])
          montant = float(row['Montant net'])
          d = comptes.setdefault(desc, {}).setdefault(sym, {})
          d.setdefault('ops', []).append((date, montant))
          d.setdefault('q', int(float(row['Quantité'])))
        elif row['Opération'] in (
            'Imp Non Res', 'Transfert', 'Vente', 'Retrait', 'Achat',
            'Cotisation'):
          # 'Cotisation': RÉER
          # 'Imp Non Res': Impôt US
          pass
        else:
          print(row['Opération'])
        if row['Commission'] != '0.00':
          print(row)
          print('  %s!' % row['Commission'])
    except csv.Error as e:
      sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
  return comptes


def print_out(comptes):
  """Fait des calculs sur le dict retourné par get_log()."""
  grand_total = 0.
  for compte, symboles in sorted(comptes.items()):
    print(compte)
    total_compte = 0.
    for symbole, d in sorted(symboles.items()):
      total_symbole = 0.
      for i, (date, montant) in enumerate(sorted(d['ops'])):
        total_symbole += montant
        total_compte += montant
        line = '  '
        if i:
          symbole = ''
        l = '  %-6s  %s %8.2f$' % (symbole, date, montant)
        if i == len(d['ops']) - 1:
          p = 0
          if d['q']:
            p = total_symbole / float(d['q'])
          l += ' %5d %8.2f$  %6.2f$/a' % (d['q'], total_symbole, p)
        print(l)

    print('  Total:             %8.2f$' % total_compte)
    if 'USD' in compte:
      # Approx
      total_compte /= 0.75
    grand_total += total_compte

  print('Grand total: %.2f$' % grand_total)


def main():
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('f', metavar='file', help='CSV to load')
  args = parser.parse_args()
  print_out(get_log(args.f))
  return 0


if __name__ == '__main__':
  sys.exit(main())
