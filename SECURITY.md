# Security Policy

## Supported Versions

Currently, the following versions are supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in GCP VM Manager, please follow these steps:

1. **Do not disclose the vulnerability publicly** until it has been addressed.
2. Email your findings to [security@yourdomain.com](mailto:security@yourdomain.com).
3. Include detailed information about the vulnerability:
   - A clear description of the issue
   - Steps to reproduce
   - Potential impact
   - Suggestions for mitigation, if any

## What to Expect

After you report a vulnerability, you can expect:

1. A confirmation email acknowledging your report within 48 hours.
2. An assessment of the vulnerability and its impact.
3. A timeline for when we expect to release a fix.
4. Notification when the vulnerability has been fixed.

## Security Considerations for Users

When using GCP VM Manager, keep the following security considerations in mind:

1. **Credentials Management**: This tool uses your local Google Cloud SDK credentials. Ensure your credentials are secured and not shared.
2. **Workspace Security**: The `config.json` file contains information about your GCP projects. Keep this file secure and do not share it.
3. **Regular Updates**: Keep the tool updated to benefit from the latest security patches.
4. **Limited Access**: Use the tool with the principle of least privilege. Configure your GCP IAM roles to only provide the necessary permissions.

## Security Features

GCP VM Manager includes the following security features:

1. **No Credential Storage**: The tool doesn't store your Google Cloud credentials; it uses the credentials provided by the Google Cloud SDK.
2. **Local Configuration**: All configuration is stored locally and not transmitted.
3. **Privacy Aware**: The tool avoids logging sensitive information.

## Vulnerability Disclosure Process

We follow a coordinated vulnerability disclosure process:

1. Security vulnerabilities are reported privately.
2. We work on fixing the vulnerability.
3. Once fixed, we release an update.
4. After users have had time to update, details of the vulnerability may be disclosed publicly. 