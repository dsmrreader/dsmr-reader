---
hide:
  - toc
---

# Upgrading v5.x to v6.x

DSMR-reader 6.x is not only incompatible, it also requires a different setup approach compared to DSMR-reader 5.x. See the schema's below for a schematic overview of both setups.

## Visual: Native setup for DSMR-reader v5.x
*All dependencies reside on the OS and required end-user to manually install/upgrade.*

``` mermaid
sequenceDiagram
    participant OS as Server (host)
    Note over OS: E.g. RaspberryPi OS
    
    create participant DSMRReader@{ "type" : "entity" }

    rect rgb(200, 150, 255)
    OS-->>DSMRReader: Hosts Supervisor to run
    Note over OS: Python
    Note over OS: Packages
    Note over DSMRReader: DSMR-reader code
    end

    create participant Database@{ "type" : "database" }
    DSMRReader->>Database: Communicates with
    
    rect rgb(191, 223, 255)
    OS-->>Database: Hosts
    Note over Database: PostgreSQL
    end
```


## Visual: New setup for DSMR-reader v6.x
*All dependencies are moved into containers and do no longer require end-user installation or upgrades.*

``` mermaid
sequenceDiagram
    participant OS as Server (host)
    Note over OS: E.g. RaspberryPi OS
    rect rgb(200, 150, 255)
    create participant REGISTRY as Docker/Podman
    OS->>REGISTRY: Runs
    end
        
    create participant DSMRReader@{ "type" : "entity" }

    rect rgb(200, 150, 255)
    REGISTRY-->>DSMRReader: Hosts DSMRReader Docker container
    Note over DSMRReader: Python
    Note over DSMRReader: Packages
    Note over DSMRReader: DSMR-reader code
    end
     
    rect rgb(200, 150, 255)
    OS<<-->>DSMRReader: Mounted volume
    Note over OS: /home/dsmrreader/dsmr_backups
    Note over DSMRReader: /app/backups
    end
    
    create participant Database@{ "type" : "database" }
    DSMRReader->>Database: Communicates with
    
    rect rgb(191, 223, 255)
    REGISTRY-->>Database: Hosts PostgreSQL container
    Note over Database: E.g. PostgreSQL
    end
    
    rect rgb(200, 150, 255)
    OS<<-->>Database: Mounted volume
    Note over OS: /home/dsmrreader/dsmr_database
    Note over Database: /var/lib/postgresql
    end
```


## Before you start
- Read the [v6 changelog](../../reference/changelog.md) for all changes. You will likely need to upgrade your database version as well.
