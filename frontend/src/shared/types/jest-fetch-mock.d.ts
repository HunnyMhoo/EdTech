declare namespace jest {
  interface Mock {
    mockResponseOnce(body: string, init?: ResponseInit): this;
    mockRejectOnce(error?: Error): this;
    resetMocks(): void;
  }
}

declare var fetch: jest.Mock; 