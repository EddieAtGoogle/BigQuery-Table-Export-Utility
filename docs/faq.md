# Frequently Asked Questions (FAQ)

## General Questions

### What is the BigQuery Table Export Utility?
The BigQuery Table Export Utility is an enterprise-grade solution for exporting large BigQuery tables to CSV format. It provides both a web interface and CLI tool for managing exports, with features like automatic file splitting, progress tracking, and secure downloads.

### What are the key features?
- Multi-interface access (Web UI, CLI, API)
- Support for large table exports (>1GB)
- Automatic file splitting and merging
- Real-time progress tracking
- Secure, authenticated downloads
- Enterprise-grade security

### What are the system requirements?
- Google Cloud project with billing enabled
- Required APIs enabled (BigQuery, Cloud Storage, Cloud Run)
- Python 3.9+ for CLI usage
- Modern web browser for UI access

## Technical Questions

### How does the export process work?
1. The utility initiates a BigQuery export job
2. BigQuery exports the data to Cloud Storage
3. Large tables are automatically split into manageable chunks
4. Progress is tracked in real-time
5. Users can download files using authenticated GCS URLs

### How are large tables handled?
- Tables are automatically split into chunks during export
- Each chunk is processed independently
- Progress is tracked for each chunk
- Downloads use efficient streaming

### What authentication methods are supported?
- Native Google Cloud authentication
- Organizational SSO (if configured)
- Command-line authentication via gcloud
- Web-based authentication flow

### How are downloads secured?
- All downloads require Google Cloud authentication
- Access is controlled through IAM permissions
- Files are accessed through authenticated GCS URLs
- All data transfer is encrypted

## Security Questions

### How are credentials handled?
- No credentials are stored by the application
- All authentication is handled through Google Cloud
- Temporary tokens are used for API access
- Service accounts follow least privilege principle

### What security best practices are implemented?
- Native Google Cloud authentication
- Fine-grained IAM roles
- Encrypted data transfer
- Audit logging
- Regular security reviews

### How is data protected?
- In-transit encryption using TLS
- At-rest encryption in Cloud Storage
- Access control through IAM
- Audit logging of all operations

## Operational Questions

### How do I monitor export jobs?
- Real-time progress in the web UI
- CLI status commands
- Cloud Run logs
- BigQuery job monitoring
- Cloud Storage metrics

### What happens if an export fails?
- Automatic retry for transient failures
- Detailed error messages
- Clean up of partial exports
- Notification in UI/CLI
- Error logging for debugging

### How do I handle timeouts for large exports?
- Exports run asynchronously
- Progress can be monitored through UI/CLI
- No timeout for the actual export process
- Downloads use streaming to handle large files

## Performance Questions

### What is the maximum table size supported?
- No hard limit on table size
- Tables are automatically split into chunks
- Tested with tables up to several TB
- Performance depends on BigQuery export speed

### How is performance optimized?
- Parallel processing of chunks
- Efficient streaming downloads
- Cloud Run automatic scaling
- BigQuery optimized exports

### What affects export speed?
- Table size and complexity
- BigQuery load
- Cloud Storage throughput
- Network conditions
- Concurrent exports

## Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Refresh credentials
gcloud auth login
gcloud auth application-default login
```

#### Permission Denied
- Verify IAM roles
- Check project permissions
- Review audit logs

#### Export Failures
- Check BigQuery job logs
- Verify storage permissions
- Monitor resource quotas

### Best Practices

#### For Large Exports
1. Use appropriate timeouts
2. Monitor progress regularly
3. Consider splitting very large tables
4. Use the CLI for better control

#### For Production Use
1. Set up monitoring
2. Configure alerts
3. Regular permission reviews
4. Maintain audit logs

## Development Questions

### How do I contribute to the project?
1. Fork the repository
2. Set up development environment
3. Make changes following guidelines
4. Submit pull request
5. See CONTRIBUTING.md for details

### How do I set up a development environment?
1. Install prerequisites
2. Clone repository
3. Configure Google Cloud project
4. Run local development server
5. See README.md for details

### How do I run tests?
```bash
# Run unit tests
python -m pytest tests/unit

# Run integration tests
python -m pytest tests/integration

# Run all tests
python -m pytest
```

## Support Questions

### Where can I get help?
1. GitHub Issues for bug reports
2. Documentation in /docs
3. Google Cloud support
4. Community forums

### How do I report bugs?
1. Check existing issues
2. Provide reproduction steps
3. Include error messages
4. Share relevant logs
5. Use issue template

### How do I request features?
1. Check planned features
2. Create feature request
3. Provide use case
4. Discuss with community

## Billing Questions

### What affects cost?
- BigQuery usage
- Cloud Storage usage
- Cloud Run compute
- Network egress
- API calls

### How can I optimize costs?
1. Clean up old exports
2. Monitor usage
3. Set up budgets
4. Use appropriate service tiers

### What billing alerts are recommended?
1. Budget alerts
2. Usage thresholds
3. Export job monitoring
4. Storage metrics

## Updates and Maintenance

### How often is the utility updated?
- Security patches: Immediate
- Bug fixes: Monthly
- Features: Quarterly
- Major versions: Annually

### How do I update the utility?
1. Check release notes
2. Backup configuration
3. Run terraform apply
4. Verify functionality
5. Update CLI if needed

### What is the versioning policy?
- Semantic versioning
- Breaking changes in major versions
- Backward compatibility in minor versions
- Security fixes in patch versions 