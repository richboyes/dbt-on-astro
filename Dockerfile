# Use the base Astro Runtime image so we can setup our CA cert before installing any packages
FROM astrocrpublic.azurecr.io/runtime:3.0-14-base

# Switch to root for setup
USER root

# Add internal CA certificate
COPY certs/netskope-cert-bundle.crt /usr/local/share/ca-certificates/netskope-cert-bundle.crt
RUN update-ca-certificates

# Make uv use system certs
ENV UV_NATIVE_TLS=1

# Install system packages if listed in packages.txt (keep if you use it)
COPY packages.txt .
RUN /usr/local/bin/install-system-packages

# Install Python dependencies from requirements.txt (Astro expects this)
COPY requirements.txt .
RUN /usr/local/bin/install-python-dependencies

# (Optional) your dbt venv step (this is fine after certs are installed)
RUN python -m venv dbt_venv && . dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-duckdb==1.8.2 dbt-snowflake==1.11.2 && deactivate

# Switch back to astro user
USER astro

# Copy project into image
COPY --chown=astro:0 . .
