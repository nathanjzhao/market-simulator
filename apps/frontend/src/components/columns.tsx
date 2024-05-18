"use client"

import { ColumnDef } from "@tanstack/react-table"

// This type is used to define the shape of our data.
export type Transaction = {
  dir: string
  id: string
  op: string
  count: string
  price: string
  symbol: string
  timestamp: number
  user: string
}

export const transactionColumns: ColumnDef<Transaction>[] = [
  {
    accessorKey: "dir",
    header: "Direction",
  },
  {
    accessorKey: "symbol",
    header: "Symbol",
  },
  {
    accessorKey: "price",
    header: "Price",
  },
  {
    accessorKey: "shares",
    header: "#",
  },
  {
    accessorKey: "op",
    header: "Operation",
  },
  {
    accessorKey: "user",
    header: "User",
  },
]

export type OrderBookSymbol = {
  dir: string
  id: string
  op: string
  count: string
  price: string
  symbol: string
  timestamp: number
  user: string
}

export const orderbookColumns: ColumnDef<OrderBookSymbol>[] = [
  {
    accessorKey: "Price",
    header: "Price",
  },
  {
    accessorKey: "Shares",
    header: "Shares",
  },
  {
    accessorKey: "Timestamp",
    header: "Timestamp",
  },
]
