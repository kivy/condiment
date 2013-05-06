Condiment
---------

Conditionally include or remove code portion, according to the environment.

For example, this is test.py:
```python
#exclude
import condiment; condiment.install()
#endexclude

if WITH_TIMEBOMB:
    print 'timebomb feature is activated'

if WITH_INAPP_PURCHASE:
    print 'inapp purchase feature is activated'

if WITH_TIMEBOMB and WITH_INAPP_PURCHASE:
    print 'both features have been activated'
```

If `WITH_TIMEBOMB` is declared in the env, all the sections concerning the
token will be included. All the others will be removed.

You can run it directly:

```
$ python test.py
$ WITH_TIMEBOMB=1 python test.py
timebomb feature is activated
$ WITH_INAPP_PURCHASE=1 WITH_TIMEBOMB=1 python test.py
timebomb feature is activated
inapp purchase feature is activated
both features have been activated
```

Or generate the output
```
$ WITH_TIMEBOMB=1 condiment test.py > output.py
$ cat output.py

print 'timebomb feature is activated'

# ----- FEATURES DEBUGGING -----
# WITH_TIMEBOMB = 1
# WITH_INAPP_PURCHASE = 
# ------------------------------
```

Related projects:

- pypreprocessor
- preprocess
