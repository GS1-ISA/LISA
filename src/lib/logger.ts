import winston, { Logform } from 'winston';
import { LoggingWinston } from '@google-cloud/logging-winston';
import { ErrorReporting } from '@google-cloud/error-reporting';

const isProduction = process.env.NODE_ENV === 'production';
const projectId = process.env.GCP_PROJECT_ID;
const sentryDsn = process.env.SENTRY_DSN;

// Initialize Google Cloud Error Reporting
const errorReporter = new ErrorReporting({
  projectId: projectId,
  serviceContext: {
    service: 'isa-frontend',
    version: process.env.GAE_VERSION || '1.0.0',
  },
  reportUnhandledExceptions: true,
});

// Configure Winston transports
const transports: winston.transport[] = [
  new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    ),
  }),
];

// Add Google Cloud Logging transport in production
if (isProduction && projectId) {
  transports.push(
    new LoggingWinston({
      projectId: projectId,
      logName: 'isa-application-log',
      resource: {
        type: 'global', // Or 'cloud_run_revision' if deployed to Cloud Run directly
        labels: {
          project_id: projectId,
        },
      },
      // Ensure full stack traces are captured for errors
      jsonFields: {
        stack_trace: (info: Logform.TransformableInfo) => info.stack,
      },
    })
  );
}

// Initialize Winston logger
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || (isProduction ? 'info' : 'debug'),
  format: winston.format.json(), // Use JSON format for structured logging
  transports: transports,
  exceptionHandlers: transports, // Send uncaught exceptions to transports
  rejectionHandlers: transports, // Send unhandled promise rejections to transports
});

// Integrate Sentry if DSN is provided
if (sentryDsn) {
  // Sentry SDK initialization would typically go here.
  // For a Next.js app, Sentry is often initialized in a separate client-side file
  // and a server-side file (e.g., Sentry.init in next.config.js or a dedicated Sentry setup file).
  // This logger would then just log to Sentry via its own transport or by Sentry's monkey-patching.
  // For simplicity here, we'll just log a message.
  logger.info('Sentry DSN found. Ensure Sentry SDK is initialized elsewhere.');
}

// Export error reporter for manual reporting if needed
export { errorReporter };
