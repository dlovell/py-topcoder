# py-topcoder
Scripts to pull down Single Round Match problems from topcoder and prepopulate python scripts with the problem text

## Usage

```
usage: topcoder.py [-h] [--divisions DIVISIONS [DIVISIONS ...]]
                   [--levels LEVELS [LEVELS ...]] [--dirname DIRNAME]
                   match_number
```


## Examples 

### Using defaults

Single Round Match (SRM) number is the only required argument.  Here we pull SRM 645 for all levels (1, 2, 3) and divisions (I, II)

> python topcoder.py 645

```
requesting http://community.topcoder.com/tc?module=MatchList at 2015-04-28 09:51:12.646979
requesting http://community.topcoder.com/stat?c=round_overview&er=5&rd=16417 at 2015-04-28 09:51:15.943469
requesting http://community.topcoder.com/stat?c=round_overview&er=5&rd=16277 at 2015-04-28 09:51:17.839005
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13603&rd=16277 at 2015-04-28 09:51:19.728588
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13346&rd=16277 at 2015-04-28 09:51:21.058975
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13347&rd=16277 at 2015-04-28 09:51:22.861156
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13604&rd=16277 at 2015-04-28 09:51:25.512117
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13602&rd=16277 at 2015-04-28 09:51:29.071618
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13349&rd=16277 at 2015-04-28 09:51:30.740384
```

Pulled files should be in `html/`, prepopulated python scripts should be in `scripts/`
> ls
```
html  problem_statement.py  problem_statement.pyc  scripts  topcoder.py
```

> ls scripts/

```
SRM645_division1_level1.py  SRM645_division1_level3.py  SRM645_division2_level2.py
SRM645_division1_level2.py  SRM645_division2_level1.py  SRM645_division2_level3.py
```

### Specifying division, dirname

You can specify which levels and divisionsyou want and what directory to write to.  Here, we say we want only division 1 (I) and we want to write the files to their own sub-directory

> python topcoder.py 643 --divisions 1 --dirname scripts/643

```
requesting http://community.topcoder.com/stat?c=round_overview&er=5&rd=16417 at 2015-04-28 10:05:11.957937
requesting http://community.topcoder.com/stat?c=round_overview&er=5&rd=16086 at 2015-04-28 10:05:14.018806
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13594&rd=16086 at 2015-04-28 10:05:14.807170
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13526&rd=16086 at 2015-04-28 10:05:15.031001
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13501&rd=16086 at 2015-04-28 10:05:15.383520
requesting http://community.topcoder.com/stat?c=problem_statement&pm=13597&rd=16086 at 2015-04-28 10:05:15.851023
requesting http://community.topcoder.com/stat?c=problem_statement&pm=12857&rd=16086 at 2015-04-28 10:05:16.103952
```

> ls scripts/643

```
SRM643_division1_level1.py  SRM643_division1_level3.py  SRM645_division1_level2.py
SRM643_division1_level2.py  SRM645_division1_level1.py  SRM645_division1_level3.py
```

Note: apparently I pull all probem statements, even if I don't write their output
