# Route53 Integration Role

AWS Route53 DNS integration for the email delivery setup playbook. This role demonstrates the DNS provider extensibility pattern and can be used as a template for adding other DNS providers.

## Overview

This role integrates AWS Route53 for automatic DNS record creation during email delivery setup. It translates the generic `dns_records` format from the main playbook into Route53 API calls.

## Features

- Automatic DNS record creation in Route53
- Support for A, MX, TXT, CNAME, and other record types
- Configurable TTL values
- Handles both root domain (@) and subdomain records
- Error handling with fallback to manual DNS instructions
- AWS credential validation

## Requirements

- AWS Account with Route53 Hosted Zone
- IAM User with Route53 permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "route53:GetChange",
          "route53:ListResourceRecordSets",
          "route53:ChangeResourceRecordSets",
          "route53:ListHostedZonesByName",
          "route53:GetHostedZone"
        ],
        "Resource": "*"
      }
    ]
  }
  ```
- Ansible 2.9+ with amazon.aws collection

## Configuration

### Variables

Set these variables in inventory or via `-e` flags:

```yaml
dns_provider: "route53"
route53_enabled: true
route53_dns_enabled: true
route53_region: "us-east-1"
route53_access_key: "YOUR_AWS_ACCESS_KEY"
route53_secret_key: "YOUR_AWS_SECRET_KEY"
```

Or use vault for credentials:

```yaml
vault_route53_access_key: "YOUR_AWS_ACCESS_KEY"
vault_route53_secret_key: "YOUR_AWS_SECRET_KEY"
```

### Usage

Basic deployment with Route53:

```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "email_domain=example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "dns_provider=route53" \
  -e "route53_region=us-east-1" \
  -e "route53_access_key=AKIAIOSFODNN7EXAMPLE" \
  -e "route53_secret_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

With vault:

```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  --ask-vault-pass \
  -e "email_domain=example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "dns_provider=route53"
```

## How It Works

1. **Record Format Translation**: Converts generic `dns_records` format to Route53 API format
2. **Zone Lookup**: Finds the Route53 Hosted Zone for the domain
3. **Record Creation**: Creates/updates DNS records via AWS API
4. **Error Handling**: Falls back to manual instructions if API calls fail

### Record Format

Input format (generic):
```yaml
dns_records:
  - zone: "example.com"        # Base zone
    record: "mail"             # Subdomain or '@' for root
    type: "A"                  # Record type
    value: "192.0.2.1"        # Record value
    ttl: 3600                  # Time to live
    state: "present"           # present/absent
```

Route53 output:
```
mail.example.com  A  192.0.2.1  (TTL: 3600)
```

## DNS Records Created

For a domain `vietcgi.nguoivietcali.com` with IP `108.181.38.69`:

1. **A Record**
   - Name: `vietcgi.nguoivietcali.com`
   - Type: A
   - Value: 108.181.38.69
   - TTL: 3600

2. **MX Record**
   - Name: `vietcgi.nguoivietcali.com`
   - Type: MX
   - Value: vietcgi.nguoivietcali.com
   - TTL: 3600

3. **SPF Record**
   - Name: `vietcgi.nguoivietcali.com`
   - Type: TXT
   - Value: v=spf1 ip4:108.181.38.69 ~all
   - TTL: 3600

4. **DMARC Record**
   - Name: `_dmarc.vietcgi.nguoivietcali.com`
   - Type: TXT
   - Value: v=DMARC1; p=none; ...
   - TTL: 3600

5. **DKIM Record**
   - Name: `default._domainkey.vietcgi.nguoivietcali.com`
   - Type: TXT
   - Value: v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3...
   - TTL: 3600

## Troubleshooting

### API Credential Errors

```
"Failed to validate AWS credentials"
```

**Solution**: Verify access key and secret key are correct

### Zone Not Found

```
"Could not find Route53 hosted zone for domain example.com"
```

**Solution**: Ensure hosted zone exists in Route53 for the domain

### Insufficient Permissions

```
"User is not authorized to perform: route53:ChangeResourceRecordSets"
```

**Solution**: Add Route53 permissions to IAM user policy

### Records Not Appearing

```
"Records created but not propagating"
```

**Note**: Route53 propagates quickly (usually < 1 minute). Check:
1. Records exist in Route53 console
2. Nameservers are properly configured
3. Domain registrar points to Route53 nameservers

## Implementation Details

This role demonstrates DNS provider extensibility by:

1. **Accepting Generic Format**: Takes `dns_records` array from main playbook
2. **Translating to Provider Format**: Converts to Route53 API format
3. **Handling Provider-Specific Features**: Uses TTL, zone ID, etc.
4. **Graceful Fallback**: Provides manual instructions if automation fails
5. **Clear Error Messages**: Reports what went wrong and suggests fixes

## For Other Providers

Use this role as a template to implement DNS providers:

1. **Cloudflare**: See `roles/cloudflare_integration/` (current implementation)
2. **Google Cloud DNS**: Similar pattern using `gcp_dns_managed_zone` module
3. **Azure DNS**: Similar pattern using `azure_rm_dnsrecordset` module
4. **Manual DNS**: Use final debug output for user to add records manually

## Testing

Dry-run test:
```bash
ansible-playbook playbooks/email-delivery-setup.yml \
  -e "email_domain=test.example.com" \
  -e "email_server_ip=192.0.2.1" \
  -e "dns_provider=route53" \
  --check -v
```

Validate records in Route53:
```bash
aws route53 list-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --region us-east-1
```

## Limitations

- Requires existing Route53 Hosted Zone
- Requires IAM user with Route53 permissions
- Does not create Hosted Zone automatically
- Does not handle Route53-specific features (health checks, failover, etc.)

## Contributing

To improve this role:

1. Test with different domain structures
2. Add support for Route53-specific features
3. Improve error messages
4. Add logging for DNS propagation tracking
5. Support Route53 alias records for AWS resources
