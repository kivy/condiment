Condiment
=========

Conditionally include or remove code portion, according to the environment. It
support offline and on-thy-fly preprocessing.

Conditional features
--------------------

Let's say you want to release a version of your code with or without a feature,
like unlimited life in a game. It can be useful during development, but you
don't want the code to be available in production.

Condiment recognize the environment variables that starts with the prefix
"WITH_" all uppercase. We could name our feature: `WITH_GODMODE`.
In python, you need to include condiment, and install it. You can put it in
exclude block, in order to be removed during the offline preprocessing.

```python
#exclude
import condiment; condiment.install()
#endexclude

class Player:

	def die(self):
		if not WITH_GODMODE:
			self.life -= 1
		return self.life
```

You can run it without the godmode:

```
$ python main.py
```

Or by activating the godmode at runtime:

```
$ WITH_GODMODE=1 python main.py
```

You can generate the final version for production too:

```
$ WITH_GODMODE=1 condiment main.py > prod_main.py
$ cat prod_main.py

class Player:

	def die(self):
		self.life -= 1
		return self.life
```

Replacing variables
-------------------

If you want to set an initial value, all the token founds in the environment
will be replaced during the generation. For example, a `WITH_LIFE` token could
have the initial number of life.

```python
#exclude
import condiment; condiment.install()
#endexclude

class Player:

	def __init__(self):
		Player.__init__(self)
		self.life = 10
		if WITH_LIFE:
			self.life = WITH_LIFE

	def die(self):
		if not WITH_GODMODE:
			self.life -= 1
		return self.life
```


Why using condiment ?
---------------------

Compared to others existing preprocessor:

- condiment doesn't rewrite the module on import, it will just inject the
  detected variables in the globals() of the module. This is avoiding double
  import of your module.
- condiment use python expression for condition (only on if)
- condiment doesn't need you to declare the variable prior the usage of them.
  Using environment variables allow you to declare them before launching the
  app, and change the behavior of your app easilly.
- condiment will replace all the variables in offline version.

Related projects
----------------

- pypreprocessor
- preprocess
