#exclude
import condiment; condiment.install()
#endexclude

if WITH_TIMEBOMB:
    timebomb = int(WITH_TIMEBOMB)
    print 'timebomb feature is activated, and set to', timebomb

if WITH_INAPP_PURCHASE:
    print 'inapp purchase feature is activated'

if WITH_TIMEBOMB and WITH_INAPP_PURCHASE:
    print 'both features have been activated'
