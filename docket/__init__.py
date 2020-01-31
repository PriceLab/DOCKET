import os
import sys
from docket.maker import DocketMaker
import docket.overview.transform as transform

# Import data fingerprints module, if available
if os.path.exists('./docket/plugins/fingerprint'):
    import docket.plugins.fingerprint as dfp
elif os.path.exists('./../docket/plugins/fingerprint'):
    import docket.plugins.fingerprint as dfp
