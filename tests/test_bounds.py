#exclude
import condiment; condiment.install()
#endexclude

def hello():
    if WITH_TIMEBOMB:
        print 'timebomb feature is activated'
        if WITH_INAPP_PURCHASE:
            print 'this would be activated only if timebomb + inapp purchase'
    if WITH_TIMEBOMB and not WITH_INAPP_PURCHASE:
        print 'only timebomb has been activated, no inapp_purchase'
    if not WITH_TIMEBOMB and WITH_INAPP_PURCHASE:
        print 'only inapp_purchase has been activated, no timebomb'
    if WITH_TIMEBOMB and WITH_INAPP_PURCHASE:
        print 'both features have been activated'
