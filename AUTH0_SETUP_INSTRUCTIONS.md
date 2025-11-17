# Auth0 M2M Setup Instructions - REQUIRED SCOPES FIX

**Status**: Token authentication working | Scopes need to be added ⚠️

---

## What We Found

Your Auth0 M2M application successfully authenticates:
- Domain: `vietcgi.us.auth0.com`
- Client ID: Valid
- Client Secret: Valid
- Token generation: Working
- **Management API scopes**: Missing or incorrectly configured

**Error**: `401 Unauthorized - Invalid token` when accessing Management API endpoints

**Cause**: The M2M app token is valid but lacks the necessary scopes to access the Management API.

---

## Fix Required: Add Management API Scopes

### Step-by-Step Instructions

**1. Go to Auth0 Dashboard**
 - Visit: https://manage.auth0.com/
 - Sign in with your account

**2. Navigate to M2M Applications**
 - Left sidebar → Applications → Applications
 - Find: Your M2M app (check the name/Client ID)

**3. Open Application Settings**
 - Click on your application name

**4. Go to "APIs" Tab**
 - Look for the APIs section in the application settings
 - You should see "Auth0 Management API"

**5. Grant All Scopes**
 - If "Auth0 Management API" is NOT listed:
 - Click "Add API"
 - Select "Auth0 Management API"

 - If it IS listed but scopes are limited:
 - Click the dropdown or settings icon next to it
 - Select the checkbox for "Expand All Scopes" OR manually check:
 - `read:clients`
 - `create:clients`
 - `update:clients`
 - `delete:clients`
 - `read:users`
 - `create:users`
 - `update:users`
 - `delete:users`
 - `read:roles`
 - `create:roles`
 - `update:roles`
 - `delete:roles`
 - `read:connections`
 - `create:connections`
 - `update:connections`
 - `delete:connections`
 - `read:permissions`
 - `create:permissions`
 - `update:permissions`
 - `delete:permissions`

**6. Save Changes**
 - Click "Save" or "Update"

**7. Test Again**
 - Run the test script again
 - Token will now include the required scopes
 - Management API endpoints should respond

---

## Why This Matters

The auth0-python SDK uses the Management API v2 to:
- Create applications
- Add users
- Configure roles
- Set up connections
- Manage permissions

Without the proper scopes, even with a valid token, Auth0 rejects all requests.

---

## Current Application Details

**Your M2M Application**:
- Domain: `vietcgi.us.auth0.com`
- Client ID: `UKa51NnAoM7uGA7TgaKpQhbxh4PD4tiv`
- Current Status: Authentication working, ⚠️ Scopes pending

---

## Testing After Fix

Once you've added the scopes:

```bash
# The framework will automatically:
# 1. Request token with all required scopes
# 2. Access Management API endpoints
# 3. Create applications, users, and roles
# 4. Configure Auth0 tenant for your client
```

---

## Scope Explanation

Each scope allows specific operations:

| Scope | Purpose |
|-------|---------|
| `read:clients` | List existing applications |
| `create:clients` | Create new applications |
| `update:clients` | Modify application settings |
| `delete:clients` | Remove applications |
| `read:users` | List existing users |
| `create:users` | Create new users |
| `update:users` | Modify user attributes |
| `delete:users` | Remove users |
| `read:roles` | List existing roles |
| `create:roles` | Create new roles |
| `update:roles` | Modify roles |
| `delete:roles` | Remove roles |
| `read:connections` | List database/social connections |
| `create:connections` | Set up new connections |

The framework needs **all of these** to:
1. Create applications for clients
2. Provision users
3. Set up role-based access control
4. Configure authentication sources

---

## After Scopes Are Added

The ansible-infra framework will:
1. Authenticate to Auth0
2. Create applications with proper OIDC settings
3. Provision users
4. Configure roles and permissions
5. Set up connections
6. Generate application configuration files
7. Store credentials securely

---

## Need Help?

**If you can't find the APIs section**:
- Check you're in the right application (M2M, not Regular Web App)
- Look for "Machine-to-Machine" label
- Try refreshing the page

**If scopes don't save**:
- Make sure you have admin access to the Auth0 tenant
- Check for "Authorization" tab instead of APIs
- Try logging out and back in

**If you want to verify scopes were added**:
- After saving, request a new token
- Decode the JWT at jwt.io
- Look for the "scope" field in the decoded token
- It should list all the permissions you added

---

**Next Action**: Add the Management API scopes, then run the test again!

