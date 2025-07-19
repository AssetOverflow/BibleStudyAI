# Use a specific version of Node.js
FROM node:22.12.0  

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Add node_modules/.bin to the PATH
ENV PATH /app/node_modules/.bin:$PATH

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 5173

# Start the application
CMD ["npm", "run", "dev"]
