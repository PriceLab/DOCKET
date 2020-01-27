import os
import sys
from docket.maker import DocketMaker

# Import data fingerprints module, if available
if os.path.exists('./docket/plugins/fingerprint/datafingerprint'):
    import docket.plugins.fingerprint.datafingerprint as dfp
elif os.path.exists('./../docket/plugins/fingerprint/datafingerprint'):
    import docket.plugins.fingerprint.datafingerprint as dfp
