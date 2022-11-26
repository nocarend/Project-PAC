import axios, { Axios } from "axios";
import { useState } from "react";
import fetchClient from "../fetchClient";

export const fromAny = () => {
    const res = fetchClient("/api/protected/fromAny")
        .then(response => {
            console.log(response.data.is_allowed, 1)
            return response.data.is_allowed
        })
        .catch(err => {
            console.log(err)
            return false
        })
   return res
}