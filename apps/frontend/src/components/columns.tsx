"use client"

import { ColumnDef } from "@tanstack/react-table"

// This type is used to define the shape of our data.
export type Transaction = {
  dir: string
  id: string
  op: string
  price: string
  symbol: string
  timestamp: number
}

export const columns: ColumnDef<Transaction>[] = [
  {
    accessorKey: "dir",
    header: "Direction",
  },
  {
    accessorKey: "symbol",
    header: "Symbol",
  },
  {
    accessorKey: "op",
    header: "Operation",
  },
  {
    accessorKey: "price",
    header: "Price",
  },
]