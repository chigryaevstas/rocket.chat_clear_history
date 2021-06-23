#!/usr/bin/env python

import datetime
import subprocess
import re


def main():
    # This grabs the current date but 30 days back
    outdate = str(datetime.datetime.now() + datetime.timedelta(days=-30))[:10]
    # This removes any messages 30+ days old
    subprocess.run(
        """rocketchat-server.mongo parties --eval 'db.rocketchat_message.remove( { ts: { $lt: ISODate(f"{outdate}") } } );'""",
        shell=True,
    )
    # This grabs any uploaded files that are 30+ days old.
    with subprocess.Popen(
        """rocketchat-server.mongo parties --eval 'db.rocketchat_uploads.find( { uploadedAt: { $lt: ISODate(f"{outdate}") } } ).forEach(printjson);'""",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ) as outerr:
        outs, errs = outerr.communicate()
        outs = str(outs)
        outs = outs.replace("\n", "").replace("\t", "")
        # This then RE the file ids out
        old_files_id = re.findall(r"\_id\"\s\:\s\"(\w+?)\"", outs)
        # iterates over the id's and removes them from the database
        for id in old_files_id:
            subprocess.run(
                """rocketchat-server.mongo parties --eval 'db.rocketchat_uploads.chunks.remove({ files_id : {$eq : f"{id}"}})'""",
                shell=True,
            )
            subprocess.run(
                """rocketchat-server.mongo parties --eval 'db.rocketchat_uploads.files.remove({ _id : {$eq : f"{id}"}})'""",
                shell=True,
            )
            subprocess.run(
                """rocketchat-server.mongo parties --eval 'db.rocketchat_uploads.remove({ _id : {$eq : f"{id}"}})'""",
                shell=True,
            )


if __name__ == "__main__":
    main()
