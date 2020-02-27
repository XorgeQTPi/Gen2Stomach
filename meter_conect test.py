
import io

import AtlasI2C_ver2

testresults = open("recent_results.txt","w")


testComponent = AtlasI2C_ver2.AtlasI2C(99,1)

curr = AtlasI2C_ver2.time.time()
end = curr +60*60*(20+2+2)

while curr <= end:
    log = testComponent.query('r')
    curr = AtlasI2C_ver2.time.time()
    log = "time:" + str(curr)+"  Returned: "+log+" \n"
    log = log.replace("\x00","")
    print(log)
    testresults.write(log)
testresults.close()
