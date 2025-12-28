# Cloudflare R2 Setup

Arch uses Cloudflare R2 for storing raw source files (PDFs, XML, ZIPs).

## Bucket Configuration

| Setting | Value |
|---------|-------|
| Bucket name | `arch` |
| Region | Auto (global) |
| Storage class | Standard |

## Directory Structure

```
arch (R2 bucket)/
├── sources/
│   ├── statutes/
│   │   ├── us/
│   │   │   ├── usc/            # US Code USLM XML
│   │   │   │   ├── 26/         # Title 26 (IRC)
│   │   │   │   ├── 7/          # Title 7 (Agriculture)
│   │   │   │   └── ...
│   │   │   └── cfr/            # Code of Federal Regulations
│   │   └── states/
│   │       ├── ny/             # New York statutes
│   │       ├── ca/             # California statutes
│   │       └── ...
│   │
│   ├── guidance/
│   │   ├── irs/
│   │   │   ├── rev-proc/       # Revenue Procedures
│   │   │   ├── rev-rul/        # Revenue Rulings
│   │   │   ├── notices/        # IRS Notices
│   │   │   └── publications/   # IRS Publications
│   │   └── usda/
│   │       └── fns/            # Food & Nutrition Service
│   │
│   ├── microdata/
│   │   ├── cps-asec/           # Current Population Survey ASEC
│   │   ├── acs/                # American Community Survey
│   │   └── scf/                # Survey of Consumer Finances
│   │
│   └── crosstabs/
│       ├── soi/                # IRS Statistics of Income
│       └── census/             # Census Bureau tables
```

## Manual Setup Instructions

The current Cloudflare API token lacks R2 permissions. To create the bucket:

### Option 1: Cloudflare Dashboard

1. Go to https://dash.cloudflare.com
2. Select your account
3. Navigate to **R2 Object Storage** in the left sidebar
4. Click **Create bucket**
5. Enter bucket name: `arch`
6. Click **Create bucket**

### Option 2: Wrangler CLI (requires new API token)

1. Create a new API token at https://dash.cloudflare.com/profile/api-tokens
2. Include these permissions:
   - **Account > Workers R2 Storage > Edit**
   - **Account > Workers R2 Storage > Read**
3. Set the token:
   ```bash
   export CLOUDFLARE_API_TOKEN="your-new-token"
   ```
4. Create the bucket:
   ```bash
   wrangler r2 bucket create arch
   ```

## API Credentials

After creating the bucket, generate R2 API credentials:

1. In R2 dashboard, go to **Manage R2 API Tokens**
2. Click **Create API token**
3. Give it a name like `arch-api`
4. Select permissions:
   - **Object Read & Write** for the `arch` bucket
5. Save the credentials:
   - Access Key ID
   - Secret Access Key

Store these in your environment or secrets manager:

```bash
# .env (local development)
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET=arch
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
```

## Python Client

Use `boto3` with S3-compatible endpoint:

```python
import boto3
import os

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
)

# Upload a file
s3.upload_file(
    'local-file.pdf',
    'arch',
    'sources/guidance/irs/rev-proc/rev-proc-2024-01.pdf'
)

# Download a file
s3.download_file(
    'arch',
    'sources/statutes/us/usc/26/32.xml',
    'local-copy.xml'
)

# List files
response = s3.list_objects_v2(
    Bucket='arch',
    Prefix='sources/guidance/irs/'
)
for obj in response.get('Contents', []):
    print(obj['Key'])
```

## Integration with Arch

The `arch` CLI will support R2 operations:

```bash
# Upload local data to R2
arch sync --to-r2

# Download from R2 to local
arch sync --from-r2

# Upload specific source type
arch sync --to-r2 --type=guidance
```

## Related Documentation

- [Source Organization](./architecture/source-organization.md) - Document structure
- [PostgreSQL Schema](../../cosilico-db/arch/README.md) - Metadata storage
