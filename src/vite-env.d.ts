/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_URL: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}

// Web Serial API type declarations
interface SerialPort {
    readonly readable: ReadableStream<Uint8Array> | null
    readonly writable: WritableStream<Uint8Array> | null
    open(options: { baudRate: number }): Promise<void>
    close(): Promise<void>
}

interface SerialPortRequestOptions {
    filters?: Array<{ usbVendorId?: number; usbProductId?: number }>
}

interface Serial {
    requestPort(options?: SerialPortRequestOptions): Promise<SerialPort>
    getPorts(): Promise<SerialPort[]>
}

interface Navigator {
    readonly serial?: Serial
}
