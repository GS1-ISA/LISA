#!/bin/bash

# SSL Certificate Generation Script for ISA_D
# This script generates self-signed certificates for development and testing

set -e

# Configuration
CERT_DIR="./ssl"
CERT_FILE="$CERT_DIR/cert.pem"
KEY_FILE="$CERT_DIR/key.pem"
DAYS_VALID=365
COUNTRY="US"
STATE="California"
LOCALITY="San Francisco"
ORGANIZATION="ISA_D"
ORGANIZATIONAL_UNIT="Development"
COMMON_NAME="localhost"
EMAIL="admin@localhost"

# Create SSL directory if it doesn't exist
mkdir -p "$CERT_DIR"

echo "Generating SSL certificate for development..."
echo "Certificate details:"
echo "  Country: $COUNTRY"
echo "  State: $STATE"
echo "  Locality: $LOCALITY"
echo "  Organization: $ORGANIZATION"
echo "  Organizational Unit: $ORGANIZATIONAL_UNIT"
echo "  Common Name: $COMMON_NAME"
echo "  Email: $EMAIL"
echo "  Validity: $DAYS_VALID days"
echo ""

# Generate private key
echo "Generating private key..."
openssl genrsa -out "$KEY_FILE" 2048

# Generate certificate signing request
echo "Generating certificate signing request..."
openssl req -new -key "$KEY_FILE" -out "$CERT_DIR/cert.csr" -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"

# Generate self-signed certificate
echo "Generating self-signed certificate..."
openssl x509 -req -days $DAYS_VALID -in "$CERT_DIR/cert.csr" -signkey "$KEY_FILE" -out "$CERT_FILE"

# Clean up CSR file
rm "$CERT_DIR/cert.csr"

# Set appropriate permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo ""
echo "SSL certificate generation completed!"
echo "Certificate: $CERT_FILE"
echo "Private Key: $KEY_FILE"
echo ""
echo "⚠️  WARNING: This is a self-signed certificate for development only!"
echo "   Do not use in production. Obtain a proper certificate from a CA."
echo ""
echo "To use with Docker:"
echo "  - Certificate volume is already configured in docker-compose.yml"
echo "  - Place certificates in ./ssl/ directory"
echo ""
echo "To use with nginx:"
echo "  - ssl_certificate /etc/nginx/ssl/cert.pem;"
echo "  - ssl_certificate_key /etc/nginx/ssl/key.pem;"