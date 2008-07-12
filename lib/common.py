import optparse

def log(text, level='INFO'):
    if level == 'INFO':
        print '>>> %s' % text
    elif level == 'ERROR':
        #print '\033[0;1m!!! Error: %s\033[m' % text
        print '!!! Error: %s' % text
    elif level == 'CMD':
        print '### %s' % text
    else:
        print text
        
def parseOptions():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    
    parser.add_option("-c", "--config", dest='config',
                      metavar="FILE", help="I will use specific config file"),
    parser.add_option("-d", "--data", dest='data',
                      metavar="FILE", help="I will use specific data directory"),
    parser.add_option("--no-prep", action="store_false",
                      dest="preparation", default=True,
                      help="Don't run first phase (web spider). I will take last "\
                      "used bucket of links")
    parser.add_option("--no-exec", action="store_false",
                      dest="execution", default=True,
                      help="Don't run second phase (execution). I won't test "\
                      "any Exit node")
    parser.add_option("--no-analyse", action="store_false",
                      dest="analysis", default=True,
                      help="Don't run third phase (analysis). I will skip "\
                      "gathering data from second phase.")

    return parser.parse_args()