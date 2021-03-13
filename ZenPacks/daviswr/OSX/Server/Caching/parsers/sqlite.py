from Products.ZenRRD.CommandParser import CommandParser


class sqlite(CommandParser):

    def processResults(self, cmd, result):
        """
        Example output:

                         bytes.dropped = 0
             bytes.fromcache.toclients = 0
               bytes.fromcache.topeers = 0
            bytes.fromorigin.toclients = 3741796533
              bytes.fromorigin.topeers = 0
             bytes.frompeers.toclients = 0
                 bytes.imported.byhttp = 0
                  bytes.imported.byxpc = 0
                    bytes.purged.total = 0
          bytes.purged.youngerthan1day = 0
        bytes.purged.youngerthan30days = 0
         bytes.purged.youngerthan7days = 0
                        imports.byhttp = 0
                         imports.byxpc = 0
           replies.fromcache.toclients = 0
             replies.fromcache.topeers = 0
          replies.fromorigin.toclients = 13
            replies.fromorigin.topeers = 0
           replies.frompeers.toclients = 0
                  requests.fromclients = 15
                    requests.frompeers = 0
        """

        values = dict()
        for line in cmd.result.output.splitlines():
            key, value = line.split(' = ')
            values[key.strip()] = int(value) if value.isdigit() else 0

        for point in cmd.points:
            if point.id in values:
                result.values.append((point, values[point.id]))
